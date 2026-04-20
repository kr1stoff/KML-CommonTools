import csv
import logging
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


def get_gene_ids(
    gene_symbols: list[str],
    gene_info_file: Union[str, Path],
) -> dict[str, str]:
    """根据NCBI gene_info文件查询基因名称对应的GeneID。

    Args:
        gene_symbols: 基因名称列表，可以是Symbol或Synonyms。
        gene_info_file: NCBI gene_info文件路径。

    Returns:
        字典，键为输入的基因名称，值为对应的GeneID（字符串）。
        如果某个基因名称未找到，则不包含在字典中。
    """
    gene_info_path = Path(gene_info_file)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    # 构建名称到GeneID的映射
    name_to_id: dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gene_id = row["GeneID"]
            symbol = row["Symbol"]
            # 添加Symbol映射（如果尚未存在）
            if symbol not in name_to_id:
                name_to_id[symbol] = gene_id

            # 添加Synonyms映射
            synonyms = row["Synonyms"]
            if synonyms and synonyms != "-":
                for syn in synonyms.split("|"):
                    syn = syn.strip()
                    if syn and syn not in name_to_id:
                        name_to_id[syn] = gene_id

    # 根据输入列表构建结果字典
    result: dict[str, str] = {}
    for symbol in gene_symbols:
        if symbol in name_to_id:
            result[symbol] = name_to_id[symbol]
        else:
            logger.debug(f"基因名称 '{symbol}' 未在gene_info文件中找到")

    return result


def get_gene_symbols(
    entrez_ids: list[str],
    gene_info_file: Union[str, Path],
) -> dict[str, str]:
    """根据NCBI gene_info文件查询Entrez ID对应的基因符号。

    Args:
        entrez_ids: Entrez ID（GeneID）列表。
        gene_info_file: NCBI gene_info文件路径。

    Returns:
        字典，键为输入的Entrez ID，值为对应的基因符号（字符串）。
        如果某个Entrez ID未找到，则不包含在字典中。
    """
    gene_info_path = Path(gene_info_file)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    # 构建Entrez ID到基因符号的映射
    id_to_symbol: dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gene_id = row["GeneID"]
            symbol = row["Symbol"]
            # 添加Entrez ID到Symbol的映射
            if gene_id not in id_to_symbol:
                id_to_symbol[gene_id] = symbol

    # 根据输入列表构建结果字典
    result: dict[str, str] = {}
    for entrez_id in entrez_ids:
        if entrez_id in id_to_symbol:
            result[entrez_id] = id_to_symbol[entrez_id]
        else:
            logger.debug(f"Entrez ID '{entrez_id}' 未在gene_info文件中找到")

    return result


if __name__ == "__main__":
    # 配置日志以显示调试信息
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

    # * 测试get_gene_ids函数
    # print("=== 测试get_gene_ids函数 ===")
    # test_genes = ["TP53", "BRCA1", "EGFR", "NOT_A_GENE", "P53"]
    # mapping = get_gene_ids(test_genes, "/data/mengxf/Database/NCBI/gene/Homo_sapiens.gene_info")
    # for gene, gene_id in mapping.items():
    #     print(f"{gene}: {gene_id}")

    print("\n=== 测试get_gene_symbols函数 ===")
    # 从上面的结果中获取一些Entrez ID进行反向测试
    test_entrez_ids = ["7157", "672", "1956", "999999"]  # TP53, BRCA1, EGFR, 不存在的ID
    symbol_mapping = get_gene_symbols(test_entrez_ids, "/data/mengxf/Database/NCBI/gene/Homo_sapiens.gene_info")
    for entrez_id, symbol in symbol_mapping.items():
        print(f"{entrez_id}: {symbol}")
