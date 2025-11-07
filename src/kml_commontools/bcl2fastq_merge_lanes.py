import click
from pathlib import Path
from multiprocessing import Pool
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@click.command()
@click.option("--input-dir", type=click.Path(exists=True), required=True, help="bcl2fastq 结果 fastq 文件夹")
@click.option("--output-dir", default="merged_fastq", show_default=True, help="合并后的 fastq 文件夹")
@click.option("--threads", default=16, show_default=True, help="并行线程数")
@click.help_option("--help", help="显示帮助信息并退出")
def merge_bcl2fastq_lanes(input_dir: str, output_dir: str, threads: int):
    """合并 bcl2fastq 生成的多条 lane 的 fastq 文件"""
    logging.info(f"开始合并 {input_dir} 中的 fastq 文件")
        
    indir = Path(input_dir).resolve()
    outdir = Path(output_dir).resolve()

    outdir.mkdir(parents=True, exist_ok=True)
    samples = list(set([fq.stem.split('_L00')[0] for fq in indir.glob('*.fastq.gz')]))

    cmds = []
    for samp in samples:
        cmds.append(
            f'zcat {indir}/{samp}_L00[12]_R1_001.fastq.gz | gzip > {outdir}/{samp}_L001_R1_001.fastq.gz')
        cmds.append(
            f'zcat {indir}/{samp}_L00[12]_R2_001.fastq.gz | gzip > {outdir}/{samp}_L001_R2_001.fastq.gz')

    with Pool(threads) as p:
        p.map(os.system, cmds)

    logging.info(f"合并完成，结果保存在 {outdir}")

if __name__ == "__main__":
    merge_bcl2fastq_lanes()
