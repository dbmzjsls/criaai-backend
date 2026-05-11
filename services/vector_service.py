"""
向量搜索服务
基于 pgvector 的产品语义搜索和相似推荐
"""
import logging
from typing import List, Optional

from sqlalchemy import text

from core.database import SessionLocal
from models.embedding import ProductEmbedding
from utils.embeddings import embedding_service

logger = logging.getLogger(__name__)


def search_similar_products(
    query: str,
    top_k: int = 10,
    category: Optional[str] = None
) -> List[dict]:
    """
    语义搜索产品

    Args:
        query: 搜索查询文本
        top_k: 返回结果数
        category: 可选的产品分类过滤

    Returns:
        产品列表 [{product_id, category, text, score, extra_data}, ...]
    """
    # 生成查询的嵌入向量
    logger.info(f"正在为查询生成嵌入向量: '{query[:60]}...' (模型: {embedding_service.MODEL})")
    query_embedding = embedding_service.embed(query)
    logger.info(f"嵌入向量生成完成, 维度: {len(query_embedding)}")

    db = SessionLocal()
    try:
        # 使用 pgvector 余弦距离 (<->)
        if category:
            results = (
                db.query(
                    ProductEmbedding,
                    ProductEmbedding.embedding.cosine_distance(query_embedding).label("score")
                )
                .filter(ProductEmbedding.category == category)
                .order_by("score")
                .limit(top_k)
                .all()
            )
        else:
            results = (
                db.query(
                    ProductEmbedding,
                    ProductEmbedding.embedding.cosine_distance(query_embedding).label("score")
                )
                .order_by("score")
                .limit(top_k)
                .all()
            )

        return [
            {
                "product_id": r.ProductEmbedding.product_id,
                "category": r.ProductEmbedding.category,
                "text": r.ProductEmbedding.text,
                "score": round(float(r.score), 4),
                "metadata": r.ProductEmbedding.extra_data,
            }
            for r in results
        ]
    finally:
        db.close()


def get_recommendations(product_id: str, top_k: int = 10) -> List[dict]:
    """
    根据产品 ID 获取相似产品推荐

    Args:
        product_id: 来源数据集中的 product_id
        top_k: 返回结果数

    Returns:
        相似产品列表（不含查询产品自身）
    """
    db = SessionLocal()
    try:
        source = (
            db.query(ProductEmbedding)
            .filter(ProductEmbedding.product_id == product_id)
            .first()
        )

        if not source:
            return []

        results = (
            db.query(
                ProductEmbedding,
                ProductEmbedding.embedding.cosine_distance(source.embedding).label("score")
            )
            .filter(ProductEmbedding.id != source.id)
            .order_by("score")
            .limit(top_k)
            .all()
        )

        return [
            {
                "product_id": r.ProductEmbedding.product_id,
                "category": r.ProductEmbedding.category,
                "text": r.ProductEmbedding.text,
                "score": round(float(r.score), 4),
                "metadata": r.ProductEmbedding.extra_data,
            }
            for r in results
        ]
    finally:
        db.close()


def get_total_count() -> int:
    """获取向量数据库中的产品总数"""
    db = SessionLocal()
    try:
        return db.query(ProductEmbedding).count()
    finally:
        db.close()


def build_rag_context(query: str, top_k: int = 5, language: str = "zh") -> str:
    """
    检索相似产品并构建 RAG 上下文，用于增强文案生成的 Prompt

    从向量数据库召回相似产品，提取品类分布和产品特征信息，
    帮助 LLM 生成更符合目标品类的营销文案。

    Args:
        query: 搜索查询（用户输入的关键词）
        top_k: 检索数量
        language: 目标语言

    Returns:
        格式化的上下文文本，无结果时返回空字符串
    """
    try:
        logger.info(f"RAG: 开始向量检索, query='{query[:60]}', top_k={top_k}")
        results = search_similar_products(query, top_k=top_k)
        logger.info(f"RAG: 检索到 {len(results)} 条相似产品")
    except Exception as e:
        logger.warning(f"RAG: 向量检索失败 - {e}")
        return ""

    if not results:
        logger.info("RAG: 无相似产品结果")
        return ""

    # 统计品类分布
    from collections import Counter
    categories = []
    for r in results:
        score = r.get("score", 1.0)
        if score > 0.8:  # 余弦距离过大=不相似，跳过
            continue
        cat = r.get("category", "")
        if cat:
            categories.append(cat)

    if not categories:
        return ""

    cat_counts = Counter(categories)
    top_category = cat_counts.most_common(1)[0][0]
    cat_display = top_category.replace("_", " ").title()

    # 构建对 LLM 有用的品类上下文
    if language == "zh":
        lines = [
            "【向量检索参考信息】",
            f"- 根据关键词语义匹配，该产品最可能属于「{cat_display}」品类",
            f"- 向量数据库中该品类的相似商品数量: {cat_counts[top_category]} 个（共检索 {len(results)} 个）",
        ]
        if len(cat_counts) > 1:
            other_cats = [f"{c.replace('_', ' ').title()}({n})" for c, n in cat_counts.most_common()[1:4]]
            lines.append(f"- 其他相关品类: {', '.join(other_cats)}")
        lines.append(f"- 请基于「{cat_display}」品类的常见文案风格和关键词进行创作\n")
    else:
        lines = [
            "[Vector Search Context]",
            f"- Closest product category: '{cat_display}'",
            f"- Similar items in this category: {cat_counts[top_category]} (out of {len(results)} retrieved)",
        ]
        if len(cat_counts) > 1:
            other_cats = [f"{c.replace('_', ' ').title()}({n})" for c, n in cat_counts.most_common()[1:4]]
            lines.append(f"- Other related categories: {', '.join(other_cats)}")
        lines.append(f"- Please tailor copywriting to the '{cat_display}' category conventions\n")

    return "\n".join(lines)
