import asyncio
import time
from datetime import datetime

from graphrag_agent.agents.fusion_agent import FusionGraphRAGAgent


TEST_CONFIG = {
    "queries": [
        "GAI-KGC 如何提升工业知识图谱构建的可控性？",
        "ASR-RAG 如何处理复杂工业问答中的多跳证据？",
    ],
    "max_wait_time": 300,
}


async def test_agent_stream(agent, agent_name, query, thread_id, max_time):
    print(f"\n[测试] {agent_name} - 流式查询: {query}")
    start_time = time.time()
    deadline = start_time + max_time
    chunks = []

    try:
        async for chunk in agent.ask_stream(query, thread_id=thread_id):
            text = chunk["answer"] if isinstance(chunk, dict) and "answer" in chunk else str(chunk)
            chunks.append(text)
            print(text, end="", flush=True)
            if time.time() > deadline:
                print("\n[提示] 达到最大等待时间，提前停止接收。")
                break
    except Exception as exc:
        print(f"\n[失败] {agent_name}: {exc}")
        return {"agent": agent_name, "query": query, "error": str(exc), "success": False}

    elapsed = time.time() - start_time
    print(f"\n[完成] 用时 {elapsed:.2f}s")
    return {"agent": agent_name, "query": query, "elapsed": elapsed, "success": True}


async def run_stream_tests():
    print(f"开始测试: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    agent = FusionGraphRAGAgent()
    results = []

    for query in TEST_CONFIG["queries"]:
        thread_id = f"fusion_stream_{int(time.time())}"
        results.append(
            await test_agent_stream(
                agent,
                "FusionGraphRAGAgent",
                query,
                thread_id,
                TEST_CONFIG["max_wait_time"],
            )
        )

    passed = sum(1 for item in results if item["success"])
    print(f"\n测试完成: {passed}/{len(results)} 成功")


if __name__ == "__main__":
    asyncio.run(run_stream_tests())
