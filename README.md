# KML-CommonTools

## 命令

- dl_seq_by_efetch: 通过 NCBI EFetch 下载序列
- prep_input_from_bcl2fastq: 从 bcl2fastq 结果文件夹中提取样本信息，生成通用分析流程输入文件
- merge_bcl2fastq_lanes: 合并 bcl2fastq 生成的不同 lane 的 fastq 文件
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
