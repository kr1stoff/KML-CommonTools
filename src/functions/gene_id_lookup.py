import csv
import logging
from pathlib import Path
from typing import Dict, List
import yaml

logger = logging.getLogger(__name__)


# 从 YAML 文件加载配置
with open(Path(__file__).parents[1] / "config/database.yaml", "r") as f:
    config = yaml.safe_load(f)
    GENE_INFO = config["GENE_INFO"]


def _parse_dbxrefs(dbxrefs_str: str) -> Dict[str, str]:
    """解析dbXrefs字符串为字典。

    Args:
        dbxrefs_str: dbXrefs字符串，格式如 "Ensembl:ENSG00000141510|HGNC:11998"

    Returns:
        解析后的字典，如 {"Ensembl": "ENSG00000141510", "HGNC": "11998"}
    """
    if not dbxrefs_str or dbxrefs_str == "-":
        return {}

    result = {}
    for item in dbxrefs_str.split("|"):
        if ":" in item:
            key, value = item.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def get_gene_ids(gene_symbols: List[str]) -> Dict[str, str]:
    """根据NCBI gene_info文件查询 Gene Symbol 对应的 Entrez ID。

    Args:
        gene_symbols: 基因名称列表，可以是Symbol或Synonyms。

    Returns:
        字典，键为输入的基因名称，值为对应的GeneID（字符串）。
        如果某个基因名称未找到，则不包含在字典中。
    """
    gene_info_path = Path(GENE_INFO)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    name_to_id: Dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gene_id = row["GeneID"]
            symbol = row["Symbol"]

            # 添加Symbol映射
            if symbol not in name_to_id:
                name_to_id[symbol] = gene_id

            # 添加Synonyms映射
            synonyms = row["Synonyms"]
            if synonyms and synonyms != "-":
                for syn in synonyms.split("|"):
                    syn = syn.strip()
                    if syn and syn not in name_to_id:
                        name_to_id[syn] = gene_id

    # 查询结果
    result: Dict[str, str] = {}
    for gene in gene_symbols:
        if gene in name_to_id:
            result[gene] = name_to_id[gene]

    return result


def get_gene_symbols(entrez_ids: List[str]) -> Dict[str, str]:
    """根据NCBI gene_info文件查询Entrez ID对应的 Gene Symbol。

    Args:
        entrez_ids: Entrez ID（GeneID）列表。

    Returns:
        字典，键为输入的Entrez ID，值为对应的基因符号（字符串）。
        如果某个Entrez ID未找到，则不包含在字典中。
    """
    gene_info_path = Path(GENE_INFO)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    id_to_symbol: Dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            gene_id = row["GeneID"]
            symbol = row["Symbol"]
            if gene_id not in id_to_symbol:
                id_to_symbol[gene_id] = symbol

    # 查询结果
    result: Dict[str, str] = {}
    for entrez_id in entrez_ids:
        if entrez_id in id_to_symbol:
            result[entrez_id] = id_to_symbol[entrez_id]

    return result


def get_ensembl_ids(gene_symbols: List[str]) -> Dict[str, str]:
    """
    根据NCBI gene_info文件查询 Gene Symbol 对应的 Ensembl ID。

    Args:
        gene_symbols: 基因名称列表，可以是Symbol或Synonyms。

    Returns:
        字典，键为输入的基因名称，值为对应的Ensembl ID（字符串）。
        如果某个基因名称未找到，则不包含在字典中。
    """
    gene_info_path = Path(GENE_INFO)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    name_to_ensembl: Dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            dbxrefs_str = row["dbXrefs"]
            if not dbxrefs_str or dbxrefs_str == "-":
                continue

            dbxrefs_dict = _parse_dbxrefs(dbxrefs_str)
            if "Ensembl" not in dbxrefs_dict:
                continue

            symbol = row["Symbol"]
            ensembl_id = dbxrefs_dict["Ensembl"]

            # 添加Symbol映射
            if symbol not in name_to_ensembl:
                name_to_ensembl[symbol] = ensembl_id

            # 添加Synonyms映射
            synonyms = row["Synonyms"]
            if synonyms and synonyms != "-":
                for syn in synonyms.split("|"):
                    syn = syn.strip()
                    if syn and syn not in name_to_ensembl:
                        name_to_ensembl[syn] = ensembl_id

    # 查询结果
    result: Dict[str, str] = {}
    for gene in gene_symbols:
        if gene in name_to_ensembl:
            result[gene] = name_to_ensembl[gene]

    return result


def get_gene_symbols_from_ensembl_id(ensembl_ids: List[str]) -> Dict[str, str]:
    """
    根据NCBI gene_info文件查询 Ensembl ID 对应的 Gene Symbol。

    Args:
        ensembl_ids: Ensembl ID 列表。

    Returns:
        字典，键为输入的Ensembl ID，值为对应的基因符号（字符串）。
        如果某个Ensembl ID未找到，则不包含在字典中。
    """
    gene_info_path = Path(GENE_INFO)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    id_to_symbol: Dict[str, str] = {}

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            dbxrefs_str = row["dbXrefs"]
            if not dbxrefs_str or dbxrefs_str == "-":
                continue

            dbxrefs_dict = _parse_dbxrefs(dbxrefs_str)
            if "Ensembl" not in dbxrefs_dict:
                continue

            symbol = row["Symbol"]
            ensembl_id = dbxrefs_dict["Ensembl"]

            # 添加Ensembl ID到Symbol的映射
            if ensembl_id not in id_to_symbol:
                id_to_symbol[ensembl_id] = symbol

    # 查询结果
    result: Dict[str, str] = {}
    for ensembl_id in ensembl_ids:
        if ensembl_id in id_to_symbol:
            result[ensembl_id] = id_to_symbol[ensembl_id]

    return result
