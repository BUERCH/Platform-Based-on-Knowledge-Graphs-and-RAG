# Test 模块

公开版测试脚本以工业知识服务场景为主，目标是做冒烟验证，而不是跑完整评测。

## 脚本说明

- `search_without_stream.py`：非流式问答测试
- `search_with_stream.py`：流式问答测试
- `test_deep_agent.py`：DeepResearchAgent 功能冒烟测试

## 运行方式

```bash
python test/search_without_stream.py
python test/search_with_stream.py
python test/test_deep_agent.py
```

## 建议前提

- 已完成 `files/industrial_demo/` 的构图
- Neo4j 已启动
- `.env` 中已配置模型服务地址和密钥
