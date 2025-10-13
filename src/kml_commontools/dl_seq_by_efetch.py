import click
from subprocess import run
from pathlib import Path
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


@click.command()
@click.option('--input-list', required=True, help='输入 Accession 列表, 每行一个')
@click.option('--efetch-path', required=True, help='efetch 程序路径')
@click.option('--output-dir', default='seq-downloads', show_default=True, help='输出文件夹')
@click.help_option(help='获取帮助信息')
def download_sequences_by_efetch(input_list, efetch_path, output_dir):
    """根据 Accession 列表下载序列"""
    Path(output_dir).resolve().mkdir(parents=True, exist_ok=True)
    with open(input_list, 'r') as f:
        accessions = [line.strip() for line in f if line.strip()]
    # ! 不能并行 efetch. "HTTP/1.1 429 Too Many Requests"
    for accession in accessions:
        cmd = f'{efetch_path} -db nuccore -format fasta -id {accession} > {output_dir}/{accession}.fasta'
        # todo 添加 stderr 检查下载是否完整
        run(cmd, shell=True, check=True)
        logging.info(f"下载 {accession} 完成")
        sleep(2)  # 设置请求间隔


if __name__ == '__main__':
    download_sequences_by_efetch()
