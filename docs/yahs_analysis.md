# yahs - 分析报告

> Yet another Hi-C scaffolding tool

## 📊 基础信息

| 项目 | 信息 |
|------|------|
| **名称** | yahs |
| **地址** | [https://github.com/c-zhou/yahs](https://github.com/c-zhou/yahs) |
| **语言** | C |
| **Stars** | 160 |
| **Forks** | 20 |
| **许可证** | MIT License |

## 👥 作者信息


- **Chenxi Zhou** (chnx.zhou@gmail.com)

- **cz370 cz370** (cz370@login-e-9.data.cluster)

- **c-zhou** (chnx.zhou@gmail.com)


## 📚 相关发表文章


暂无相关发表文章信息。


## 🔧 功能特性

### 主要用途
YaHS是一个利用Hi-C数据进行基因组scaffolding的工具，旨在区分真实的Hi-C相互作用信号与比对噪声。

### 核心功能

- 基于Hi-C信号拓扑分布的新算法，用于检测contig连接

- 生成的scaffold通常具有更高的N90和L90统计值

- 运行速度快，例如在5分钟内完成人类基因组重建


### 支持格式

**输入格式**: `FASTA`, `BAM`, `BED`, `PA5`, `BIN`

**输出格式**: `AGP`, `FASTA`

### 主要依赖

- `C编译器`

- `GNU make`

- `zlib开发文件`


## 🏗️ 项目架构


### 编程语言

- `Shell`

- `C`


### 框架/库


### 入口点

- 可执行脚本: run_test.sh

- 可执行脚本: run_yahs.sh


### 目录结构

- **kalloc.h**: 根目录文件

- **LICENSE**: 根目录文件

- **yahs.c**: 根目录文件

- **README.md**: 根目录文件

- **.git**: 普通目录

- **kopen.c**: 根目录文件

- **Makefile**: 根目录文件

- **binomlite.c**: 根目录文件

- **kdq.h**: 根目录文件

- **bamlite.h**: 根目录文件

- **break.c**: 根目录文件

- **graph.h**: 根目录文件

- **graph.c**: 根目录文件

- **asset.h**: 根目录文件

- **telo.h**: 根目录文件

- **asset.c**: 根目录文件

- **sdict.c**: 根目录文件

- **.gitignore**: 根目录文件

- **break.h**: 根目录文件

- **scripts**: 脚本目录

- **telo.c**: 根目录文件

- **link.h**: 根目录文件

- **sdict.h**: 根目录文件

- **enzyme.c**: 根目录文件

- **link.c**: 根目录文件

- **kalloc.c**: 根目录文件

- **juicer.c**: 根目录文件

- **ksort.h**: 根目录文件

- **cov.c**: 根目录文件

- **bamlite.c**: 根目录文件

- **version.h**: 根目录文件

- **agp-spec.h**: 根目录文件

- **khash.h**: 根目录文件

- **kseq.h**: 根目录文件

- **ketopt.h**: 根目录文件

- **agp_to_fasta.c**: 根目录文件

- **enzyme.h**: 根目录文件

- **cov.h**: 根目录文件

- **kvec.h**: 根目录文件



## 💻 代码质量



## ⚡ 性能特征


### 性能指标

- **时间复杂度**: 未明确提及，但代码中涉及多个模块化组件，如链表、图处理和统计模型。
- **空间复杂度**: 需要支持C编译的环境，依赖zlib库。
- **并行化支持**: 支持将输入文件转换为二进制BIN格式以减少IO开销 支持直接通过管道输入数据
- **资源使用**: 需要支持C编译的环境，依赖zlib库。

### 优化建议



## 🧬 生物信息学专业性



## 👋 可用性



## 💻 使用方法

### 安装方法
```bash
git clone https://github.com/c-zhou/yahs.git && make
```

### 基本用法
```bash
yahs contigs.fa hic-to-contigs.bam
```


### 使用示例

```bash
yahs contigs.fa hic-to-contigs.bam
```





---

*分析时间: 2025-09-07T16:22:37.065440*  
*报告由 BioTools Agent 自动生成*
        