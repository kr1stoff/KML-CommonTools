#!/usr/bin/env python3
import click
import pandas as pd
import datetime
from pathlib import Path
import warnings
# 忽略 openpyxl.reader.workbook 模块中的 UserWarning
warnings.filterwarnings('ignore', category=UserWarning,
                        module='openpyxl.reader.workbook')


@click.command()
@click.argument('info_file', type=click.Path(exists=True))
@click.argument('out_file', type=click.Path())
@click.help_option("--help", help="显示帮助信息并退出")
def haobo_info_rec_to_samplesheet(info_file, out_file):
    """
    将信息记录转换为样本表

    \b
    INFO_FILE: 输入上机信息表文件路径
    OUT_FILE: 输出 samplesheet 文件路径
    """
    click.echo(f"处理文件: {info_file}")
    click.echo(f"输出到: {out_file}")
    # 读取 samplesheet 模板文件
    ss_template_file = Path(__file__).parents[1].joinpath(
        'assets/samplesheet-template-v5.csv')
    ss_template = open(ss_template_file).read()
    # 获取今天日期 2026/2/4 格式
    today = datetime.datetime.now().strftime("%Y/%m/%d")
    # 读取样本信息表获取样本 index 信息
    df = pd.read_excel(info_file, sheet_name='上机文库pooling表（修改后）',
                       skiprows=13, usecols='C,D,E')
    # 写 samplesheet
    with open(out_file, 'w') as f:
        f.write(ss_template.format(date=today))
        for _, row in df.iterrows():
            if is_index(row['Index(P5)']):
                f.write(
                    f"{row['实验号\n(建库)']},,,,,{row['Index(P7)']},,{row['Index(P5)']},,\n")


def is_index(index_string):
    "检查 index 是否只包含 A、T、C、G 四种碱基"
    if not isinstance(index_string, str):
        return False
    for char in index_string:
        if char not in ['A', 'T', 'C', 'G']:
            return False
    return True


if __name__ == '__main__':
    haobo_info_rec_to_samplesheet()
