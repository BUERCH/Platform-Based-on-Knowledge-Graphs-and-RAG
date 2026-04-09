import asyncio
import os
import sys
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc


WORKING_DIR = str(PROJECT_ROOT / "examples" / "output" / "industrial_demo_cache")


async def llm_model_func(
    prompt: str,
    system_prompt: str | None = None,
    history_messages: list[dict] | None = None,
    **kwargs,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return await openai_complete_if_cache(
        model,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )


async def embedding_func(texts: list[str]) -> np.ndarray:
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_API_BASE") or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set.")
    return await openai_embed(
        texts,
        model=model,
        api_key=api_key,
        base_url=base_url,
    )


async def initialize_rag() -> LightRAG:
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=int(os.getenv("EMBEDDING_DIM", "1536")),
            max_token_size=8192,
            func=embedding_func,
        ),
    )
    await rag.initialize_storages()
    return rag


async def answer_question() -> None:
    rag = await initialize_rag()
    try:
        question = os.getenv(
            "DEMO_QUESTION",
            "GAI-KGC 和 ASR-RAG 在工业知识服务平台中分别承担什么角色？",
        )

        for mode in ["naive", "local", "global", "hybrid"]:
            response = await rag.aquery(
                question,
                param=QueryParam(mode=mode, stream=False),
            )
            print(f"\n[{mode}]")
            print(response)
    finally:
        await rag.finalize_storages()


if __name__ == "__main__":
    asyncio.run(answer_question())
