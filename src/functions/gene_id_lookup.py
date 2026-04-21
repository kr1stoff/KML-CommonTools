import csv
import logging
from pathlib import Path
from typing import Union, Optional, Dict, List, Tuple
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=128)
def _get_gene_info_file_stats(gene_info_file: str) -> Tuple[float, int]:
    """获取gene_info文件的统计信息用于缓存失效检测。

    Args:
        gene_info_file: gene_info文件路径

    Returns:
        (修改时间戳, 文件大小) 元组
    """
    path = Path(gene_info_file)
    if not path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {path}")
    return (path.stat().st_mtime, path.stat().st_size)


def _validate_gene_info_file(gene_info_file: Union[str, Path]) -> Path:
    """验证gene_info文件是否存在并返回Path对象。

    Args:
        gene_info_file: gene_info文件路径

    Returns:
        Path对象

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    gene_info_path = Path(gene_info_file)
    if not gene_info_path.exists():
        raise FileNotFoundError(f"gene_info文件不存在: {gene_info_path}")

    # 记录文件访问日志
    logger.debug(f"访问gene_info文件: {gene_info_path}")
    return gene_info_path


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


@lru_cache(maxsize=32)
def _build_name_to_value_mapping_cached(
    gene_info_file: str,
    value_column: str = "GeneID",
    include_synonyms: bool = True,
    filter_func_name: Optional[str] = None,
    value_transform_func_name: Optional[str] = None,
) -> Dict[str, str]:
    """带缓存的基因名称到指定值的映射构建函数。

    Args:
        gene_info_file: gene_info文件路径
        value_column: 要映射的值所在的列名
        include_synonyms: 是否包含同义词
        filter_func_name: 可选的行过滤函数名称（用于缓存键）
        value_transform_func_name: 可选的值转换函数名称（用于缓存键）

    Returns:
        名称到值的映射字典
    """
    gene_info_path = Path(gene_info_file)
    name_to_value: Dict[str, str] = {}

    logger.debug(f"构建映射: file={gene_info_file}, column={value_column}, "
                f"include_synonyms={include_synonyms}")

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        row_count = 0
        mapped_count = 0

        for row in reader:
            row_count += 1

            # 应用过滤函数（如果提供）
            if filter_func_name:
                # 这里简化处理，实际应用中需要根据函数名称调用对应函数
                # 由于缓存限制，这里只记录过滤状态
                pass

            value = row[value_column]
            symbol = row["Symbol"]

            # 添加Symbol映射（如果尚未存在）
            if symbol not in name_to_value:
                name_to_value[symbol] = value
                mapped_count += 1

            # 添加Synonyms映射
            if include_synonyms:
                synonyms = row["Synonyms"]
                if synonyms and synonyms != "-":
                    for syn in synonyms.split("|"):
                        syn = syn.strip()
                        if syn and syn not in name_to_value:
                            name_to_value[syn] = value
                            mapped_count += 1

    logger.debug(f"映射构建完成: 处理{row_count}行, 生成{mapped_count}个映射")
    return name_to_value


def _build_name_to_value_mapping(
    gene_info_path: Path,
    value_column: str = "GeneID",
    include_synonyms: bool = True,
    filter_func: Optional[callable] = None,
    value_transform_func: Optional[callable] = None,
) -> Dict[str, str]:
    """构建基因名称到指定值的映射。

    Args:
        gene_info_path: gene_info文件路径
        value_column: 要映射的值所在的列名
        include_synonyms: 是否包含同义词
        filter_func: 可选的行过滤函数
        value_transform_func: 可选的值转换函数

    Returns:
        名称到值的映射字典
    """
    # 获取文件统计信息用于缓存
    file_key = str(gene_info_path)

    # 为简单起见，这里不使用复杂的函数名称缓存
    # 在实际应用中，可以根据需要添加更复杂的缓存逻辑
    return _build_name_to_value_mapping_cached(
        file_key,
        value_column,
        include_synonyms
    )


@lru_cache(maxsize=32)
def _build_id_to_symbol_mapping_cached(gene_info_file: str) -> Dict[str, str]:
    """带缓存的Entrez ID到基因符号的映射构建函数。

    Args:
        gene_info_file: gene_info文件路径

    Returns:
        Entrez ID到基因符号的映射字典
    """
    gene_info_path = Path(gene_info_file)
    id_to_symbol: Dict[str, str] = {}

    logger.debug(f"构建ID到Symbol映射: file={gene_info_file}")

    with open(gene_info_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        row_count = 0

        for row in reader:
            row_count += 1
            gene_id = row["GeneID"]
            symbol = row["Symbol"]
            # 添加Entrez ID到Symbol的映射
            if gene_id not in id_to_symbol:
                id_to_symbol[gene_id] = symbol

    logger.debug(f"ID到Symbol映射构建完成: 处理{row_count}行, 生成{len(id_to_symbol)}个映射")
    return id_to_symbol


def _build_id_to_symbol_mapping(gene_info_path: Path) -> Dict[str, str]:
    """构建Entrez ID到基因符号的映射。

    Args:
        gene_info_path: gene_info文件路径

    Returns:
        Entrez ID到基因符号的映射字典
    """
    return _build_id_to_symbol_mapping_cached(str(gene_info_path))


def _query_mapping(
    query_items: List[str],
    mapping: Dict[str, str],
    item_type: str = "基因名称"
) -> Dict[str, str]:
    """根据映射字典查询结果。

    Args:
        query_items: 要查询的项目列表
        mapping: 映射字典
        item_type: 项目类型（用于日志记录）

    Returns:
        查询结果字典
    """
    result: Dict[str, str] = {}
    for item in query_items:
        if item in mapping:
            result[item] = mapping[item]
        else:
            logger.debug(f"{item_type} '{item}' 未在gene_info文件中找到")
    return result


def get_gene_ids(
    gene_symbols: List[str],
    gene_info_file: Union[str, Path],
) -> Dict[str, str]:
    """根据NCBI gene_info文件查询 Gene Symbol 对应的 Entrez ID。

    Args:
        gene_symbols: 基因名称列表，可以是Symbol或Synonyms。
        gene_info_file: NCBI gene_info文件路径。

    Returns:
        字典，键为输入的基因名称，值为对应的GeneID（字符串）。
        如果某个基因名称未找到，则不包含在字典中。
    """
    gene_info_path = _validate_gene_info_file(gene_info_file)
    name_to_id = _build_name_to_value_mapping(gene_info_path, value_column="GeneID")
    return _query_mapping(gene_symbols, name_to_id, "基因名称")


def get_gene_symbols(
    entrez_ids: List[str],
    gene_info_file: Union[str, Path],
) -> Dict[str, str]:
    """根据NCBI gene_info文件查询Entrez ID对应的 Gene Symbol。

    Args:
        entrez_ids: Entrez ID（GeneID）列表。
        gene_info_file: NCBI gene_info文件路径。

    Returns:
        字典，键为输入的Entrez ID，值为对应的基因符号（字符串）。
        如果某个Entrez ID未找到，则不包含在字典中。
    """
    gene_info_path = _validate_gene_info_file(gene_info_file)
    id_to_symbol = _build_id_to_symbol_mapping(gene_info_path)
    return _query_mapping(entrez_ids, id_to_symbol, "Entrez ID")


def get_ensembl_ids(
    gene_symbols: List[str],
    gene_info_file: Union[str, Path],
) -> Dict[str, str]:
    """
    根据NCBI gene_info文件查询 Gene Symbol 对应的 Ensembl ID。

    Args:
        gene_symbols: 基因名称列表，可以是Symbol或Synonyms。
        gene_info_file: NCBI gene_info文件路径。

    Returns:
        字典，键为输入的基因名称，值为对应的Ensembl ID（字符串）。
        如果某个基因名称未找到，则不包含在字典中。
    """
    gene_info_path = _validate_gene_info_file(gene_info_file)

    # 由于缓存函数的限制，我们需要单独处理Ensembl ID的提取
    # 先获取所有包含Ensembl ID的行的映射
    name_to_dbxrefs: Dict[str, str] = {}

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
            if symbol not in name_to_dbxrefs:
                name_to_dbxrefs[symbol] = ensembl_id

            # 添加Synonyms映射
            synonyms = row["Synonyms"]
            if synonyms and synonyms != "-":
                for syn in synonyms.split("|"):
                    syn = syn.strip()
                    if syn and syn not in name_to_dbxrefs:
                        name_to_dbxrefs[syn] = ensembl_id

    return _query_mapping(gene_symbols, name_to_dbxrefs, "基因名称")


def run_tests():
    """运行所有测试函数。"""
    # 配置日志以显示调试信息
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")

    test_file = "/data/mengxf/Database/NCBI/gene/Homo_sapiens.gene_info"

    print("=" * 60)
    print("基因ID查询函数测试")
    print("=" * 60)

    # 测试1: get_gene_ids函数
    print("\n1. 测试 get_gene_ids 函数 (Gene Symbol → Entrez ID)")
    print("-" * 40)
    test_genes = ["TP53", "BRCA1", "EGFR", "NOT_A_GENE", "P53"]
    try:
        mapping = get_gene_ids(test_genes, test_file)
        print(f"查询基因: {test_genes}")
        print(f"找到 {len(mapping)}/{len(test_genes)} 个基因:")
        for gene, gene_id in mapping.items():
            print(f"  {gene}: {gene_id}")
    except Exception as e:
        print(f"测试失败: {e}")

    # 测试2: get_gene_symbols函数
    print("\n2. 测试 get_gene_symbols 函数 (Entrez ID → Gene Symbol)")
    print("-" * 40)
    test_entrez_ids = ["7157", "672", "1956", "999999"]
    try:
        symbol_mapping = get_gene_symbols(test_entrez_ids, test_file)
        print(f"查询Entrez ID: {test_entrez_ids}")
        print(f"找到 {len(symbol_mapping)}/{len(test_entrez_ids)} 个ID:")
        for entrez_id, symbol in symbol_mapping.items():
            print(f"  {entrez_id}: {symbol}")
    except Exception as e:
        print(f"测试失败: {e}")

    # 测试3: get_ensembl_ids函数
    print("\n3. 测试 get_ensembl_ids 函数 (Gene Symbol → Ensembl ID)")
    print("-" * 40)
    test_genes = ["TP53", "BRCA1", "EGFR", "NOT_A_GENE", "P53", "ABCC6P2"]
    try:
        ensembl_mapping = get_ensembl_ids(test_genes, test_file)
        print(f"查询基因: {test_genes}")
        print(f"找到 {len(ensembl_mapping)}/{len(test_genes)} 个基因的Ensembl ID:")
        for gene, ensembl_id in ensembl_mapping.items():
            print(f"  {gene}: {ensembl_id}")
    except Exception as e:
        print(f"测试失败: {e}")

    # 测试4: 性能测试（缓存效果）
    print("\n4. 性能测试（缓存效果）")
    print("-" * 40)
    import time

    # 第一次调用
    start_time = time.time()
    result1 = get_gene_ids(["TP53", "BRCA1"], test_file)
    first_call_time = time.time() - start_time

    # 第二次调用（应该从缓存读取）
    start_time = time.time()
    result2 = get_gene_ids(["TP53", "BRCA1"], test_file)
    second_call_time = time.time() - start_time

    print(f"第一次调用时间: {first_call_time:.4f}秒")
    print(f"第二次调用时间: {second_call_time:.4f}秒")
    print(f"缓存加速: {first_call_time/second_call_time:.1f}x")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
