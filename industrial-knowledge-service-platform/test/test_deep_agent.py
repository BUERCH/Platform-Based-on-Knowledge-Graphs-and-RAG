import asyncio
import json

from graphrag_agent.agents.deep_research_agent import DeepResearchAgent


async def main():
    agent = DeepResearchAgent(use_deeper_tool=True)

    print("=== DeepResearchAgent 冒烟测试 ===")

    print("\n--- 流式回答 ---")
    async for chunk in agent.ask_stream(
        "ASR-RAG 如何将子图检索与推理链编排结合起来？",
        show_thinking=False,
    ):
        if isinstance(chunk, dict) and "answer" in chunk:
            print("\n[最终答案]")
            print(chunk["answer"])
        else:
            print(chunk, end="", flush=True)

    print("\n--- 思考过程 ---")
    thinking_result = agent.ask_with_thinking("GAI-KGC 如何控制工业知识图谱的构建质量？")
    print(thinking_result.get("answer", ""))
    print(f"执行日志条数: {len(thinking_result.get('execution_logs', []))}")

    if hasattr(agent, "explore_knowledge"):
        print("\n--- 知识探索 ---")
        exploration = agent.explore_knowledge("工业知识服务平台的核心模块")
        print(json.dumps(exploration, ensure_ascii=False, indent=2)[:800])

    if hasattr(agent, "analyze_reasoning_chain"):
        print("\n--- 推理链分析 ---")
        analysis = agent.analyze_reasoning_chain()
        print(json.dumps(analysis, ensure_ascii=False, indent=2)[:800])

    if hasattr(agent, "detect_contradictions"):
        print("\n--- 证据冲突分析 ---")
        contradictions = agent.detect_contradictions("证据治理不足会带来哪些平台风险？")
        print(json.dumps(contradictions, ensure_ascii=False, indent=2)[:800])


if __name__ == "__main__":
    asyncio.run(main())
