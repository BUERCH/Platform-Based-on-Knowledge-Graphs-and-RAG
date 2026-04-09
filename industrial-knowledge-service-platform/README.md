# 工业知识服务平台原型

本项目是论文《基于知识图谱的 RAG 知识服务平台设计与实现》的公开版平台原型。仓库保留了可运行的后端、前端、GraphRAG 构建流程和工业知识样例，用于展示论文中的三条主线如何落到工程实现：

- `GAI-KGC`：离线知识图谱构建、候选生成、裁决与证据治理。
- `ASR-RAG`：在线自适应子图检索、证据拼接与推理链组织。
- `Industrial Knowledge Service Platform`：可解释问答、证据卡片、子图可视化与平台服务接口。

## 公开版定位

- 保留真实可运行代码和轻量工业样例，便于 GitHub 展示与答辩说明。
- 默认使用 [`files/industrial_demo`](./files/industrial_demo) 中的公开演示文档进行构图和问答。
- 有意省略完整工业语料、私有提示模板、闭源评估集、全量实验超参数，因此外部读者可以运行演示，但不能完全复现实验结果。

## 目录说明

```text
industrial-knowledge-service-platform/
|-- graphrag_agent/          # 核心包：图谱构建、检索、Agent、评估
|-- server/                  # FastAPI 后端
|-- frontend/                # Streamlit 前端
|-- files/industrial_demo/   # 公开工业演示数据
|-- test/                    # 面向公开版的冒烟测试脚本
|-- assets/industrial-platform-quickstart.md  # 快速开始说明
|-- .env.example             # 公开版环境变量模板
`-- setup.py                 # 包元信息
```

## 快速开始

1. 创建 Python 3.10 环境并安装依赖。
2. 启动 Neo4j。
3. 复制 `.env.example` 为 `.env`，填写自己的模型服务地址和密钥。
4. 运行构图流程，把 `files/industrial_demo/` 导入图数据库。
5. 启动后端和前端进行演示。

示例命令：

```bash
conda create -n industrial-kg python=3.10 -y
conda activate industrial-kg
pip install -r requirements.txt
pip install -e .

docker compose up -d

python graphrag_agent/integrations/build/main.py
python server/main.py
streamlit run frontend/app.py
```

更完整的步骤见 [`assets/industrial-platform-quickstart.md`](./assets/industrial-platform-quickstart.md)。

## 建议演示问题

- `GAI-KGC 如何控制工业知识图谱构建质量？`
- `ASR-RAG 如何将子图检索与证据链推理结合起来？`
- `工业知识服务平台包含哪些核心模块？`
- `证据治理为什么对工业问答可信性重要？`

## 论文映射

- 第 3 章对应离线图谱构建能力，体现在 `graphrag_agent/graph/` 和 `graphrag_agent/integrations/build/`。
- 第 4 章对应图增强检索与推理能力，体现在 `graphrag_agent/search/`、`graphrag_agent/agents/`。
- 第 5 章对应平台集成与交互展示，体现在 `server/`、`frontend/` 与公开样例数据组织。

## 公开仓库边界

本仓库适合展示平台架构、模块划分、基础构图与在线问答流程。若要获得与论文完全一致的实验结论，仍需要未公开的工业语料、内部评测配置和私有提示工程资源。
