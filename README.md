# KML-CommonTools

## 命令

### haobo_info_rec_to_samplesheet

浩博项目固定模板上机信息表转 illumina samplesheet

```bash
poetry run haobo-info-rec-to-samplesheet 20260211-高通量测序仪Nextseq\ 500\ 样本上机信息记录表v4.0.xlsx test-samplesheet.csv
```

### prep_input_from_bcl2fastq

从 bcl2fastq 结果文件夹中提取样本信息，生成通用分析流程输入文件

```bash
poetry run prep-input-from-bcl2fastq --input-dir /data/mengxf/Project/KML260107_HAOBOHBV_AH5C55AFXC/FASTQ --output-file /data/mengxf/Project/KML260107_HAOBOHBV_AH5C55AFXC/FASTQ/input.tsv
```

### dl_seq_by_efetch

通过 NCBI EFetch 下载序列

### merge_bcl2fastq_lanes

合并 bcl2fastq 生成的不同 lane 的 fastq 文件

### simu_fq_by_vcf

使用 vcf 模拟 fastq 文件

```bash
# 野生型
poetry run python -m src.kml_commontools.simu_fq_by_vcf \
  --input-ref /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251029-ref/ref/D00330.fasta \
  --output-prefix /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251028-simu/bwt \
  --wild-type \
  --region D00330.1:1-2000
# 纯合变异型
poetry run python -m src.kml_commontools.simu_fq_by_vcf \
    --input-ref /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251029-ref/ref/D00330.fasta \
    --input-vcf /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251010-simu-1500/input-vcfs/mut7.vcf \
    --output-prefix /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251028-simu/bmut7vaf100 \
    --variant-allele-freq 1 \
    --region D00330.1:1-2000
```

### rnaseq_ensg_convert_symbol

将表达矩阵的行名从 Ensembl ID 转换为 Gene Symbol

```bash
poetry run python -m src.kml_commontools.rnaseq_ensg_convert_symbol \
    --input-file /data/mengxf/Project/KML250122-rnaseq-ZiYan/result/250731/feature_counts/gene_count.tsv \
    --mart-tab /data/mengxf/Database/reference/hg38/mart_export.txt \
    --output-file /data/mengxf/Temp/gene-symbol-count.tsv
```

## 函数

### 获取基因 ID

输入基因列表, 返回基因 ID 映射字典.
 `conda develop` 安装在了 `python3.12` 环境下，可直接导入使用：

```python
from gene_id_lookup import get_gene_ids

gene_list = ["TP53", "BRCA1", "EGFR", "NOT_A_GENE", "P53"]
mapping = get_gene_ids(gene_list)
```
