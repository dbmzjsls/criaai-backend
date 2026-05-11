"""
向量嵌入服务
使用 Dashscope Text Embedding SDK (text-embedding-v3)
"""
import logging
import time
from typing import List

from dashscope import TextEmbedding

from core.config import settings


class EmbeddingService:
    """Dashscope 文本嵌入服务"""

    MODEL = "text-embedding-v4"

    def __init__(self):
        self.api_key = settings.DASHSCOPE_API_KEY

    def embed(self, text: str) -> List[float]:
        """
        为单条文本生成嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量 (List[float])
        """
        response = TextEmbedding.call(
            model=self.MODEL,
            input=text,
            text_type="document",
            api_key=self.api_key,
        )
        if response.status_code != 200:
            raise Exception(
                f"Embedding API error (HTTP {response.status_code}): {response.message}"
            )
        output = response.output
        if isinstance(output, dict):
            return output["embeddings"][0]["embedding"]
        return output.embeddings[0].embedding

    def embed_batch(
        self, texts: List[str], max_retries: int = 3, batch_size: int = 10
    ) -> List[List[float]]:
        """
        批量生成嵌入向量

        Args:
            texts: 文本列表
            max_retries: 最大重试次数
            batch_size: 每批文本数

        Returns:
            嵌入向量列表
        """
        if not texts:
            return []

        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            embeddings = None

            for attempt in range(max_retries):
                try:
                    response = TextEmbedding.call(
                        model=self.MODEL,
                        input=batch,
                        text_type="document",
                        api_key=self.api_key,
                    )
                    if response.status_code == 200:
                        output = response.output
                        if isinstance(output, dict):
                            embeddings = [e["embedding"] for e in output["embeddings"]]
                        else:
                            embeddings = [e.embedding for e in output.embeddings]
                        break
                    else:
                        err_msg = f"HTTP {response.status_code}: {response.message}"
                        if response.status_code == 429:
                            wait = (2 ** attempt) * 2
                            logging.getLogger(__name__).info(f"速率限制，等待 {wait}s...")
                            time.sleep(wait)
                            continue
                        raise Exception(f"API error: {err_msg}")
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise Exception(
                            f"Batch [{i}:{i+len(batch)}] 失败 ({max_retries}次重试): {e}"
                        )
                    time.sleep(2 ** attempt)

            if embeddings is None:
                raise Exception(f"Batch [{i}:{i+len(batch)}] 所有重试均失败")

            all_embeddings.extend(embeddings)
            # 进度输出
            total_done = min(i + len(batch), len(texts))
            if total_done % 500 == 0 or total_done == len(texts):
                logging.getLogger(__name__).info(f"嵌入进度: {total_done}/{len(texts)}")

            # 批次间小延迟，避免速率限制
            time.sleep(0.15)

        return all_embeddings


# 全局单例
embedding_service = EmbeddingService()
