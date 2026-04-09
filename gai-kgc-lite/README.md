# GAI-KGC Lite

`GAI-KGC Lite` 是论文《基于知识图谱的RAG知识服务平台设计与实现》中第三章方法 `GAI-KGC` 的公开演示版工程，聚焦工业知识图谱构建、证据绑定、图数据库导入与图分析。

## 公开版边界

这个仓库保留了可运行的轻量流程，但不提供以下内容：

- 完整工业语料与标注集
- 私有提示模板与全部实验参数
- 在线模型服务密钥
- 用于论文复现实验的全量评测脚本

因此外部用户可以运行 demo、查看工程结构与处理结果，但无法一键完整复现实验。

## 当前目录结构

- `data/`
  - 公开样例工业文档
- `output/`
  - 已生成的实体、三元组与摘要结果
- `gai_kgc_workflow_demo.ipynb`
  - 公开版流程 notebook，已清理输出并移除硬编码密钥
- `generate_demo_report.py`
  - 离线汇总当前公开结果，生成 `output/gai_kgc_public_demo_report.md`
- `import_to_neo4j.py`
  - 将抽取结果导入 Neo4j，支持 `--dry-run`
- `analyze_graph.py`
  - 基于 Neo4j 图数据做中心性分析

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

生成公开版结果报告：

```bash
python generate_demo_report.py
```

只做导入预检查，不连接数据库：

```bash
python import_to_neo4j.py --dry-run
```

导入 Neo4j：

```bash
$env:NEO4J_URI="neo4j://127.0.0.1:7687"
$env:NEO4J_USERNAME="neo4j"
$env:NEO4J_PASSWORD="your_password"
python import_to_neo4j.py
```

分析图中关键节点：

```bash
python analyze_graph.py --top-k 15
```

## 样例数据说明

公开版数据以“新型电力系统信息物理安全防护”相关文本作为工业语料代理，用于展示：

- 长文档切分后的知识抽取结果
- 工业实体与关系的组织形式
- 图导入、图分析与公开报告生成流程

## 作者信息

- Thesis adaptation / public release: `Pei Jicheng`
- Method chapter mapping: `Chapter 3 - GAI-KGC`
