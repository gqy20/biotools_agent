# yahs - 分析报告

> Yet another Hi-C scaffolding tool

## 📊 基础信息

| 项目 | 信息 |
|------|------|
| **名称** | yahs |
| **地址** | [https://github.com/c-zhou/yahs](https://github.com/c-zhou/yahs) |
| **语言** | C |
| **Stars** | 158 |
| **Forks** | 20 |
| **许可证** | MIT License |

## 👥 作者信息


- **Chenxi Zhou** (chnx.zhou@gmail.com)

- **cz370 cz370** (cz370@login-e-9.data.cluster)

- **c-zhou** (chnx.zhou@gmail.com)


## 📚 相关发表文章



### 未说明

- **作者**: 
- **期刊**: 未说明

- **DOI**: [https://zenodo.org/badge/latestdoi/411044095](https://doi.org/https://zenodo.org/badge/latestdoi/411044095)




## 🔧 功能特性

### 主要用途
利用Hi-C数据进行基因组scaffolding的工具

### 核心功能

- 基于Hi-C信号拓扑分布的新contig连接检测算法

- 生成更连续的scaffold，具有更高的N90和L90统计值

- 运行速度快，重建人类基因组仅需不到5分钟


### 支持格式

**输入格式**: `FASTA`, `BAM`, `BED`, `PA5`, `BIN`

**输出格式**: `AGP`, `FASTA`

### 主要依赖

- `C编译器`

- `GNU make`

- `zlib开发文件`


## 💻 使用方法

### 安装方法
```bash
下载源代码并运行`make`命令进行编译
```

### 基本用法
```bash
yahs contigs.fa hic-to-contigs.bam
```


### 使用示例

```bash
yahs contigs.fa hic-to-contigs.bam
```




### 主要参数

- -o: 指定输出文件前缀

- -a: 指定AGP文件进行scaffolding

- -r: 指定分辨率范围

- -R: 指定每个分辨率级别的运行轮数

- -e: 指定Hi-C实验使用的限制性内切酶

- -l: 指定用于scaffolding的最小contig长度

- -q: 设置最小读取映射质量

- --no-contig-ec: 跳过初始组装错误校正步骤

- --no-scaffold-ec: 跳过scaffolding错误检查

- --no-mem-check: 禁用运行时内存检查

- --file-type: 指定输入文件格式

- --read-length: 指定HiC数据的读取长度



---

*分析时间: 2025-08-12T22:02:53.305371*  
*报告由 BioTools Agent 自动生成*
        