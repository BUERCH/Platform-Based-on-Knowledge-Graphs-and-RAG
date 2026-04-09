import time
from datetime import datetime

from graphrag_agent.agents.fusion_agent import FusionGraphRAGAgent


TEST_CONFIG = {
    "queries": [
        "GAI-KGC 的核心流程包括哪些阶段？",
        "ASR-RAG 如何组织图谱与文本证据？",
        "工业知识服务平台为什么需要证据治理？",
    ]
}


def test_agent(agent, agent_name, query, thread_id):
    print(f"\n[测试] {agent_name} - 查询: {query}")
    try:
        start_time = time.time()
        answer = agent.ask(query, thread_id=thread_id)
        execution_time = time.time() - start_time
        print(f"[完成] 用时 {execution_time:.2f}s")
        print(answer)
        return {
            "agent": agent_name,
            "query": query,
            "execution_time": execution_time,
            "success": True,
        }
    except Exception as exc:
        print(f"[失败] {agent_name}: {exc}")
        return {
            "agent": agent_name,
            "query": query,
            "error": str(exc),
            "success": False,
        }


def run_tests():
    print(f"开始测试: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    agent = FusionGraphRAGAgent()
    results = []

    for query in TEST_CONFIG["queries"]:
        thread_id = f"fusion_{int(time.time())}"
        results.append(test_agent(agent, "FusionGraphRAGAgent", query, thread_id))

    passed = sum(1 for item in results if item["success"])
    print(f"\n测试完成: {passed}/{len(results)} 成功")


if __name__ == "__main__":
    run_tests()
