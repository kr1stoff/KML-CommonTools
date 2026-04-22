from src.functions.gene_id_lookup import get_gene_ids, get_gene_symbols, get_ensembl_ids, get_gene_symbols_from_ensembl_id


def run_tests():
    """运行所有测试函数。"""
    print("=" * 60)
    print("基因ID查询函数测试")
    print("=" * 60)

    # 测试1: get_gene_ids函数
    print("\n1. 测试 get_gene_ids 函数 (Gene Symbol → Entrez ID)")
    print("-" * 40)
    test_genes = ["TP53", "BRCA1", "EGFR", "NOT_A_GENE", "P53"]
    try:
        mapping = get_gene_ids(test_genes)
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
        symbol_mapping = get_gene_symbols(test_entrez_ids)
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
        ensembl_mapping = get_ensembl_ids(test_genes)
        print(f"查询基因: {test_genes}")
        print(f"找到 {len(ensembl_mapping)}/{len(test_genes)} 个基因的Ensembl ID:")
        for gene, ensembl_id in ensembl_mapping.items():
            print(f"  {gene}: {ensembl_id}")
    except Exception as e:
        print(f"测试失败: {e}")

    # 测试4：get_gene_symbols_from_ensembl_id函数
    print("\n4. 测试 get_gene_symbols_from_ensembl_id 函数 (Ensembl ID → Gene Symbol)")
    print("-" * 40)
    test_ensembl_ids = ["ENSG00000141510", "ENSG00000012048",
                        "ENSG00000133703", "ENSG00000284332"]
    try:
        symbol_mapping = get_gene_symbols_from_ensembl_id(
            test_ensembl_ids)
        print(f"查询Ensembl ID: {test_ensembl_ids}")
        print(f"找到 {len(symbol_mapping)}/{len(test_ensembl_ids)} 个ID:")
        for ensembl_id, symbol in symbol_mapping.items():
            print(f"  {ensembl_id}: {symbol}")
    except Exception as e:
        print(f"测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
