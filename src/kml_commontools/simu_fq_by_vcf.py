import click
import logging
import subprocess
import shutil
import math
from dataclasses import dataclass
from typing import Union, Optional
from pathlib import Path
from Bio import SeqIO

from src.config.software import DWGSIM, SAMTOOLS, BWA, SEQTK, SEQKIT

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")


@click.command()
@click.option("--input-ref", type=click.Path(exists=True), required=True, help="参考基因组 fasta 文件")
@click.option("--input-vcf", type=click.Path(exists=True), help="变异 vcf 文件")
@click.option("--output-prefix", default="simu-out", show_default=True,
              help="输出文件前缀, 输出双端 fastq 文件. 输出文件: <output-prefix>_1.fq.gz 和 <output-prefix>_2.fq.gz")
@click.option("--wild-type", is_flag=True, help="仅模拟参考基因组序列的测序数据. 如果指定该参数, 则忽略 --input-vcf 和 --variant-allele-freq 参数")
@click.option("--variant-allele-freq", default=0.05, show_default=True, help="变异等位基因频率, 仅在指定了 --input-vcf 时有效")
@click.option("--region", required=True, help="指定基因组区域进行模拟, 格式: chr:start-end")
@click.option("--data-volumn", default=500000000, show_default=True, help="模拟数据量, 单位: bp")
@click.option("--read-length", type=int, default=150, show_default=True, help="读取长度")
@click.option("--threads", type=int, default=4, show_default=True, help="使用的线程数")
@click.help_option("--help", help="显示帮助信息并退出")
def simulate_fastq_by_vcf(input_ref, input_vcf, output_prefix, wild_type, variant_allele_freq,
                          region, data_volumn, read_length, threads):
    """通过参考基因组 fasta 文件和变异 vcf 文件模拟测序数据, 输出双端 fastq 文件"""
    simu_fq_by_vcf = SimulateFastqByVcf(
        input_ref=input_ref,
        output_prefix=output_prefix,
        wild_type=wild_type,
        variant_allele_freq=variant_allele_freq,
        region=region,
        data_volumn=data_volumn,
        read_length=read_length,
        threads=threads,
        input_vcf=input_vcf,
    )
    simu_fq_by_vcf.simulate()


@dataclass
class SimulateFastqByVcf:
    input_ref: Union[str, Path]
    output_prefix: Union[str, Path]
    wild_type: bool
    variant_allele_freq: float
    region: str
    data_volumn: int
    read_length: int
    threads: int
    input_vcf: Optional[Union[str, Path]] = None

    def __post_init__(self):
        self.name = Path(self.output_prefix).stem
        self.outdir = Path(self.output_prefix).parent
        self.tmpdir = self.outdir / f".tmp-{self.name}"
        self.tmpdir.mkdir(parents=True, exist_ok=True)
        self.filter_paired_reads_script = Path(__file__).parents[1] / \
            "util/simu_fq_by_vcf-filter_paired_reads_by_qname.pl"
        self.single_read_num = math.ceil(
            self.data_volumn / self.read_length / 2)
        self.out_read1 = Path(f"{self.output_prefix}_1.fq.gz")
        self.out_read2 = Path(f"{self.output_prefix}_2.fq.gz")
        # 检查参考基因组 fasta 文件, 区域, vcf 序列 id 是否一致
        self.check_ref_id()

    def check_ref_id(self) -> None:
        """检查参考基因组 fasta 文件, 区域, vcf 序列 id 是否一致"""
        logging.info("检查参考基因组 fasta 文件, 区域, vcf 序列 id 是否一致")
        self.seqid = list(SeqIO.parse(self.input_ref, "fasta"))[0].id
        # region 检查
        if not self.region.startswith(self.seqid):
            raise click.ClickException(
                f"区域 {self.region} 序列 id 与参考基因组 fasta 文件 {self.input_ref} 序列 id 不一致")
        # vcf 检查
        if self.input_vcf:
            with open(self.input_vcf) as f:
                content = f.read()
            if self.seqid not in content:
                raise click.ClickException(
                    f"vcf 文件 {self.input_vcf} 序列 id 与参考基因组 fasta 文件 {self.input_ref} 序列 id 不一致")

    def remove_temporary_dir(self) -> None:
        """删除临时目录"""
        logging.info("删除临时目录")
        if (self.out_read1.stat().st_size > 100) and (self.out_read2.stat().st_size > 100):
            shutil.rmtree(self.tmpdir)

    def simulate_wild_type(self):
        """仅模拟参考基因组序列的测序数据, 输出双端 fastq 文件"""
        logging.info("仅模拟参考基因组序列的测序数据, 输出双端 fastq 文件")
        # 检查参考基因组 fasta 文件, 区域是否一致
        cmd = f"""#!/bin/bash
# 模拟数据
{DWGSIM} -y 0 -e 0 -E 0 -r 0 -R 0 -N 10000 -1 {self.read_length} -2 {self.read_length} \
    {self.input_ref} \
    {self.tmpdir}/dwgsim
# 比对数据
{BWA} mem -t {self.threads} -M -Y -R '@RG\\tID:{self.name}\\tPL:illumina\\tSM:{self.name}' \
    {self.input_ref} \
    {self.tmpdir}/dwgsim.bwa.read1.fastq.gz \
    {self.tmpdir}/dwgsim.bwa.read2.fastq.gz \
    | {SAMTOOLS} view -@ 4 -hbS - \
    | {SAMTOOLS} sort -@ 4 -o {self.tmpdir}/align.bam - 
{SAMTOOLS} index {self.tmpdir}/align.bam
# 圈定 target 区域
{SAMTOOLS} view -h {self.tmpdir}/align.bam {self.region} \
    | perl {self.filter_paired_reads_script} \
    > {self.tmpdir}/target.sam
# 提取 target 区域的 fastq 文件
{SAMTOOLS} fastq \
    -1 {self.tmpdir}/target_reads_align.1.fq.gz \
    -2 {self.tmpdir}/target_reads_align.2.fq.gz \
    {self.tmpdir}/target.sam
# 重复, 改序列名称, 并排序
# ! 数据量如果超过 1G, 酌情调整 times 参数
# read1
{SEQKIT} dup --times 2000 \
    {self.tmpdir}/target_reads_align.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw1.1.fq.gz
{SEQKIT} rename \
    {self.tmpdir}/target_reads_dupfq.raw1.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw2.1.fq.gz
{SEQKIT} sort --threads {self.threads} --by-name \
    {self.tmpdir}/target_reads_dupfq.raw2.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.1.fq.gz
# read2
{SEQKIT} dup --times 2000 \
    {self.tmpdir}/target_reads_align.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw1.2.fq.gz
{SEQKIT} rename \
    {self.tmpdir}/target_reads_dupfq.raw1.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw2.2.fq.gz
{SEQKIT} sort --threads {self.threads} --by-name \
    {self.tmpdir}/target_reads_dupfq.raw2.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.2.fq.gz
# 野生型
{SEQTK} sample \
    {self.tmpdir}/target_reads_dupfq.1.fq.gz \
    {self.single_read_num} | \
    gzip --force > {self.out_read1}
{SEQTK} sample \
    {self.tmpdir}/target_reads_dupfq.2.fq.gz \
    {self.single_read_num} | \
    gzip --force > {self.out_read2}
"""
        # 执行命令
        self.write_and_run_cmd(cmd)

    def simulate_hom(self):
        """模拟纯合变异, 输出双端 fastq 文件"""
        logging.info("模拟纯合变异, 输出双端 fastq 文件")
        cmd = f"""#!/bin/bash
# 模拟数据
{DWGSIM} -N 10000 -y 0 -e 0 -E 0 -r 0 -R 0 -1 {self.read_length} -2 {self.read_length} \
    -v {self.input_vcf} \
    {self.input_ref} \
    {self.tmpdir}/dwgsim
# 比对数据
{BWA} mem -t {self.threads} -M -Y -R '@RG\\tID:{self.name}\\tPL:illumina\\tSM:{self.name}' \
    {self.input_ref} \
    {self.tmpdir}/dwgsim.bwa.read1.fastq.gz \
    {self.tmpdir}/dwgsim.bwa.read2.fastq.gz \
    | {SAMTOOLS} view -@ {self.threads} -hbS - \
    | {SAMTOOLS} sort -@ {self.threads} -o {self.tmpdir}/align.bam -
{SAMTOOLS} index {self.tmpdir}/align.bam
# 圈定 target 区域
{SAMTOOLS} view -h {self.tmpdir}/align.bam {self.region} \
    | perl {self.filter_paired_reads_script} \
    > {self.tmpdir}/target.sam 
# 提取 target 区域的 fastq 文件
{SAMTOOLS} fastq \
    -1 {self.tmpdir}/target_reads_align.1.fq.gz \
    -2 {self.tmpdir}/target_reads_align.2.fq.gz \
    {self.tmpdir}/target.sam
# 重复, 改序列名称, 并排序
# ! 数据量如果超过 1G, 酌情调整 times 参数
# read1
{SEQKIT} dup --times 2000 \
    {self.tmpdir}/target_reads_align.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw1.1.fq.gz
{SEQKIT} rename \
    {self.tmpdir}/target_reads_dupfq.raw1.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw2.1.fq.gz
{SEQKIT} sort --threads {self.threads} --by-name \
    {self.tmpdir}/target_reads_dupfq.raw2.1.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.1.fq.gz
# read2
{SEQKIT} dup --times 2000 \
    {self.tmpdir}/target_reads_align.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw1.2.fq.gz
{SEQKIT} rename \
    {self.tmpdir}/target_reads_dupfq.raw1.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.raw2.2.fq.gz
{SEQKIT} sort --threads {self.threads} --by-name \
    {self.tmpdir}/target_reads_dupfq.raw2.2.fq.gz \
    --out-file {self.tmpdir}/target_reads_dupfq.2.fq.gz
# 纯合变异性
{SEQTK} sample \
    {self.tmpdir}/target_reads_dupfq.1.fq.gz \
    {self.single_read_num} | \
    gzip --force > {self.out_read1}
{SEQTK} sample \
    {self.tmpdir}/target_reads_dupfq.2.fq.gz \
    {self.single_read_num} | \
    gzip --force > {self.out_read2}
"""
        # 执行命令
        self.write_and_run_cmd(cmd)

    def write_and_run_cmd(self, cmd: str) -> None:
        """写入并运行 bash 命令"""
        with open(self.tmpdir / "simulate.sh", "w") as f:
            f.write(cmd)
        res = subprocess.run(f"bash {self.tmpdir / 'simulate.sh'}",
                             shell=True, check=True, capture_output=True, text=True)
        # 标准输出和标准错误
        with open(self.tmpdir / "simulate.log", "w") as f:
            f.write(res.stdout + '\n' + res.stderr)

    def simulate(self):
        """模拟测序数据"""
        if self.wild_type:
            self.simulate_wild_type()
        elif self.variant_allele_freq == 1:
            self.simulate_hom()
        # TODO 模拟杂合突变
        # TODO 开发完解除注释
        # self.remove_temporary_dir()


if __name__ == "__main__":
    simulate_fastq_by_vcf()
