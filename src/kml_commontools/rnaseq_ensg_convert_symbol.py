import click
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@click.command()
@click.option("--input-file", type=click.Path(exists=True), required=True,
              help="输入的表达矩阵文件, 第一列为 Ensembl ID, 列名为 Geneid")
@click.option("--mart-tab", type=click.Path(exists=True), required=True,
              help="BioMart 导出的表格文件，包含 Ensembl ID 到 Gene Symbol 的映射")
@click.option("--output-file", default="gene-symbol-count.tsv", show_default=True,
              help="输出的转换后的表达矩阵文件")
@click.help_option("--help", help="显示帮助信息并退出")
def convert_ensg_to_symbol(input_file: str, mart_tab: str, output_file: str):
    """将表达矩阵的行名从Ensembl ID转换为Gene Symbol"""
    logging.info(f"从 {input_file} 中读取表达矩阵")
    df = pd.read_csv(input_file, sep="\t")
    logging.info(f"从 {mart_tab} 中读取 BioMart 映射表格并去重")
    mapdf = pd.read_csv(mart_tab, sep="\t", usecols=["Gene stable ID", "Gene name"])
    mapdf.drop_duplicates(inplace=True)
    mapdf.rename(columns={"Gene stable ID": "Geneid", "Gene name": "Symbol"}, inplace=True)
    logging.info(f"合并表达矩阵和 BioMart 映射表格")
    outdf = pd.merge(df, mapdf, on="Geneid", how="left").fillna("")
    outdf[["Symbol"] + list(df.columns)].to_csv(output_file, sep="\t", index=False)
    logging.info(f"完成，共处理 {len(outdf)} 个基因")


if __name__ == "__main__":
    convert_ensg_to_symbol()
