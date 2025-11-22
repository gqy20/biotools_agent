# picard - 分析报告

> A set of command line tools (in Java) for manipulating high-throughput sequencing (HTS) data and formats such as SAM/BAM/CRAM and VCF.

## 📊 基础信息

| 项目 | 信息 |
|------|------|
| **名称** | picard |
| **地址** | [https://github.com/broadinstitute/picard](https://github.com/broadinstitute/picard) |
| **语言** | Java |
| **Stars** | 1037 |
| **Forks** | 382 |
| **许可证** | MIT License |

## 👥 作者信息


- **Yossi Farjoun** (yossi@fulcrumgenomics.com)

- **kachulis** (39926576+kachulis@users.noreply.github.com)

- **Louis Bergelson** (louisb@broadinstitute.org)

- **UC Ngwudike** (63610971+ungwudik@users.noreply.github.com)

- **Ilya Soifer** (ilya.soifer@ultimagen.com)

- **Pontus Höjer** (pontus.hojer@scilifelab.se)

- **Kevin Lydon** (KevinCLydon@gmail.com)

- **Ethan Nelson-Moore** (nelsonmo@usc.edu)

- **Gökalp Çelik** (37572619+gokalpcelik@users.noreply.github.com)

- **Dror Kessler** (dror27.kessler@gmail.com)


## 📚 相关发表文章


暂无相关发表文章信息。


## 🔧 功能特性

### 主要用途
生物信息学工具

### 核心功能


### 支持格式

**输入格式**: 

**输出格式**: 

### 主要依赖


## 🏗️ 项目架构


### 编程语言

- `Shell`

- `R`

- `Java`

- `Python`

- `JavaScript`


### 框架/库


### 入口点


### 目录结构

- **docs**: 文档目录

- **docs/fingerprinting**: 普通目录

- **src**: 源代码目录

- **src/main**: 普通目录

- **src/main/java**: 普通目录

- **src/main/java/picard**: 普通目录

- **src/main/resources**: 普通目录

- **src/main/resources/picard**: 普通目录

- **src/test**: 测试目录

- **src/test/java**: 普通目录

- **src/test/java/picard**: 普通目录

- **src/test/resources**: 普通目录

- **etc**: 普通目录

- **etc/test**: 测试目录

- **LICENSE.txt**: 根目录文件

- **README.md**: 根目录文件

- **.git**: 普通目录

- **.gitattributes**: 根目录文件

- **build_push_docker.sh**: 根目录文件

- **.dockerignore**: 根目录文件

- **.github**: 普通目录

- **build.xml**: 根目录文件

- **Dockerfile**: 根目录文件

- **.gitignore**: 根目录文件

- **scripts**: 脚本目录

- **scripts/travis**: 普通目录

- **testdata**: 普通目录

- **testdata/picard**: 普通目录

- **testdata/picard/fastq**: 普通目录

- **testdata/picard/fingerprint**: 普通目录

- **testdata/picard/fingerprint/index_test**: 普通目录

- **testdata/picard/quality**: 普通目录

- **testdata/picard/arrays**: 普通目录

- **testdata/picard/arrays/illumina**: 普通目录

- **testdata/picard/sam**: 普通目录

- **testdata/picard/sam/SplitSamByNumberOfReads**: 普通目录

- **testdata/picard/sam/CleanSam**: 普通目录

- **testdata/picard/sam/MergeSamFiles**: 普通目录

- **testdata/picard/sam/FixMateInformation**: 普通目录

- **testdata/picard/sam/QualityScoreDistribution**: 普通目录

- **testdata/picard/sam/bam2fastq**: 普通目录

- **testdata/picard/sam/FilterSamReads**: 普通目录

- **testdata/picard/sam/AlignmentSummaryMetrics**: 普通目录

- **testdata/picard/sam/fastq2bam**: 普通目录

- **testdata/picard/sam/InsertSizeMetrics**: 普通目录

- **testdata/picard/sam/MarkDuplicates**: 普通目录

- **testdata/picard/sam/BamErrorMetrics**: 普通目录

- **testdata/picard/sam/ValidateSamFile**: 普通目录

- **testdata/picard/sam/CollectGcBiasMetrics**: 普通目录

- **testdata/picard/sam/MeanQualityByCycle**: 普通目录

- **testdata/picard/sam/CheckDuplicateMarking**: 普通目录

- **testdata/picard/sam/RnaSeqMetrics**: 普通目录

- **testdata/picard/sam/PositionalDownsampleSam**: 普通目录

- **testdata/picard/sam/CollectQualityYieldMetrics**: 普通目录

- **testdata/picard/sam/DownsampleSam**: 普通目录

- **testdata/picard/sam/AddOATag**: 普通目录

- **testdata/picard/sam/CollectRrbsMetrics**: 普通目录

- **testdata/picard/sam/SamFormatConverterTest**: 普通目录

- **testdata/picard/sam/CompareSAMs**: 普通目录

- **testdata/picard/sam/RevertSam**: 普通目录

- **testdata/picard/sam/EstimateLibraryComplexity**: 普通目录

- **testdata/picard/sam/BaseDistributionByCycle**: 普通目录

- **testdata/picard/sam/MergeBamAlignment**: 普通目录

- **testdata/picard/sam/GatherBamFiles**: 普通目录

- **testdata/picard/vcf**: 普通目录

- **testdata/picard/vcf/chunking**: 普通目录

- **testdata/picard/vcf/GatherVcf**: 普通目录

- **testdata/picard/vcf/filter**: 普通目录

- **testdata/picard/vcf/FixVcfHeaderTest**: 普通目录

- **testdata/picard/vcf/LiftOver**: 普通目录

- **testdata/picard/vcf/MakeVcfSampleNameMap**: 普通目录

- **testdata/picard/reference**: 普通目录

- **testdata/picard/metrics**: 普通目录

- **testdata/picard/independent_replicates**: 普通目录

- **testdata/picard/indices**: 普通目录

- **testdata/picard/annotation**: 普通目录

- **testdata/picard/annotation/SortGff**: 普通目录

- **testdata/picard/analysis**: 普通目录

- **testdata/picard/analysis/directed**: 普通目录

- **testdata/picard/analysis/metrics**: 普通目录

- **testdata/picard/analysis/artifacts**: 普通目录

- **testdata/picard/analysis/TheoreticalSensitivity**: 普通目录

- **testdata/picard/flow**: 普通目录

- **testdata/picard/flow/reads**: 普通目录

- **testdata/picard/util**: 工具目录

- **testdata/picard/util/largeScattersWithRemainder**: 普通目录

- **testdata/picard/util/largeScatters**: 普通目录

- **testdata/picard/util/largeScattersNoRemainder**: 普通目录

- **testdata/picard/util/BedToIntervalListTest**: 普通目录

- **testdata/picard/illumina**: 普通目录

- **testdata/picard/illumina/readerTests**: 普通目录

- **testdata/picard/illumina/CollectIlluminaBasecallingMetrics**: 普通目录

- **testdata/picard/illumina/CollectIlluminaLaneMetrics**: 普通目录

- **testdata/picard/illumina/125T125T**: 普通目录

- **testdata/picard/illumina/25T8B8B25T_hiseqx**: 普通目录

- **testdata/picard/illumina/151T8B8B151T_cbcl**: 普通目录

- **testdata/picard/illumina/IlluminaLaneMetricsCollectorTest**: 普通目录

- **testdata/picard/illumina/25T8B8B25T**: 普通目录

- **testdata/picard/illumina/parserTests**: 普通目录

- **testdata/picard/illumina/25T8B25T**: 普通目录

- **build.gradle**: 根目录文件

- **settings.gradle**: 根目录文件

- **gradle**: 普通目录

- **gradle/wrapper**: 普通目录

- **gradlew**: 根目录文件



## 💻 代码质量



## ⚡ 性能特征



## 🧬 生物信息学专业性



## 👋 可用性



## 🔒 安全风险分析


### 安全风险概览

| 风险级别 | 数量 |
|----------|------|
| **高风险** | 0 |
| **中风险** | 0 |
| **低风险** | 0 |

**扫描工具**: `bandit`




### 安全建议


- 未发现明显的安全问题，建议定期进行安全检查



*扫描时间: 2025-11-22T15:54:57.520186*


## 💻 使用方法

### 安装方法
```bash
参考项目文档
```

### 基本用法
```bash
参考项目文档
```





---

*分析时间: 2025-11-22T15:54:57.428889*  
*报告由 BioTools Agent 自动生成*
        