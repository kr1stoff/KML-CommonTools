# KML-CommonTools

## 命令

- dl_seq_by_efetch: 通过 NCBI EFetch 下载序列
- bcl2fastq_prep_input_from: 从 bcl2fastq 结果文件夹中提取样本信息，生成通用分析流程输入文件
- bcl2fastq_merge_lanes: 合并 bcl2fastq 生成的不同 lane 的 fastq 文件
- simu_fq_by_vcf: 使用 vcf 模拟 fastq 文件
  - 野生型

    ```bash
    poetry run python -m src.kml_commontools.simu_fq_by_vcf \
      --input-ref /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251029-ref/ref/D00330.fasta \
      --output-prefix /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251028-simu/bwt \
      --wild-type \
      --region D00330.1:1-2000
    ```

  - 纯合变异型

    ```bash
    poetry run python -m src.kml_commontools.simu_fq_by_vcf \
        --input-ref /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251029-ref/ref/D00330.fasta \
        --input-vcf /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251010-simu-1500/input-vcfs/mut7.vcf \
        --output-prefix /data/mengxf/Project/KML250919-HAOBOHBV-PIPELINE-YANZHENG/work/251028-simu/bmut7vaf100 \
        --variant-allele-freq 1 \
        --region D00330.1:1-2000
    ```

- rnaseq_ensg_convert_symbol: 将表达矩阵的行名从 Ensembl ID 转换为 Gene Symbol

    ```bash
    poetry run python -m src.kml_commontools.rnaseq_ensg_convert_symbol \
        --input-file /data/mengxf/Project/KML250122-rnaseq-ZiYan/result/250731/feature_counts/gene_count.tsv \
        --mart-tab /data/mengxf/Database/reference/hg38/mart_export.txt \
        --output-file /data/mengxf/Temp/gene-symbol-count.tsv
    ```
