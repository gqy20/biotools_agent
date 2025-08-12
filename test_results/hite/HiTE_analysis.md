# HiTE - 分析报告

> High-precision TE Annotator

## 📊 基础信息

| 项目 | 信息 |
|------|------|
| **名称** | HiTE |
| **地址** | [https://github.com/CSU-KangHu/HiTE](https://github.com/CSU-KangHu/HiTE) |
| **语言** | Python |
| **Stars** | 122 |
| **Forks** | 5 |
| **许可证** | GNU General Public License v3.0 |

## 👥 作者信息


- **Kang Hu** (kanghu@csu.edu.cn)


## 📚 相关发表文章



### 未说明

- **作者**: 
- **期刊**: 未说明

- **DOI**: [未说明](https://doi.org/未说明)




## 🔧 功能特性

### 主要用途
HiTE用于基因组组装中完整长度转座元件（TE）的检测与注释，采用动态边界调整方法，具有快速且准确的特点。

### 核心功能

- 动态边界调整方法检测完整长度TE

- 支持多种安装方式（Conda, Docker, Singularity, Nextflow）

- 提供panHiTE流程用于大规模群体基因组TE检测


### 支持格式

**输入格式**: `FASTA (.fasta, .fa, .fna)`

**输出格式**: `FASTA (.fa)`, `GFF`, `OUT`, `TBL`

### 主要依赖

- `Python 3`

- `Conda`

- `Docker`

- `Singularity`

- `Nextflow`


## 💻 使用方法

### 安装方法
```bash
支持多种安装方式：
1. Git克隆项目仓库
2. 使用Conda创建环境并运行configure.py
3. 使用Singularity拉取镜像
4. 使用Docker拉取镜像
5. 使用Nextflow运行工作流
```

### 基本用法
```bash
python main.py --genome <genome_file> --thread <num_threads> --out_dir <output_directory>
```


### 使用示例

```bash
python main.py --genome /home/hukang/HiTE/demo/genome.fa --thread 40 --out_dir /home/hukang/HiTE/demo/test/
```

```bash
singularity run -B /home/hukang:/home/hukang /home/hukang/HiTE.sif python /HiTE/main.py --genome /home/hukang/HiTE/demo/genome.fa --thread 40 --out_dir /home/hukang/HiTE/demo/test/
```




### 主要参数

- --genome: 指定输入基因组文件（FASTA格式）

- --thread: 指定运行线程数

- --out_dir: 指定输出目录

- --curated_lib: 提供可信的TE库用于预掩码

- --annotate: 使用HiTE生成的TE库进行基因组注释

- --domain: 是否预测TE中的保守蛋白结构域



---

*分析时间: 2025-08-12T22:06:14.842910*  
*报告由 BioTools Agent 自动生成*
        