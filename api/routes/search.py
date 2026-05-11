"""
向量搜索 API 路由
提供语义产品搜索和相似推荐接口
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from services.vector_service import (
    search_similar_products,
    get_recommendations,
    get_total_count,
)

router = APIRouter(prefix="/api/v1/search", tags=["向量搜索"])


class SearchRequest(BaseModel):
    query: str = Field(..., description="搜索查询文本", min_length=1)
    top_k: int = Field(10, ge=1, le=100, description="返回结果数")
    category: str | None = Field(None, description="产品分类过滤")


class ProductResult(BaseModel):
    product_id: str
    category: str | None
    text: str
    score: float
    metadata: dict | None


class SearchResponse(BaseModel):
    results: list[ProductResult]
    total: int


class StatsResponse(BaseModel):
    total_products: int
    message: str


@router.post("/products", response_model=SearchResponse)
async def search_products(req: SearchRequest):
    """语义搜索产品"""
    results = search_similar_products(
        query=req.query,
        top_k=req.top_k,
        category=req.category,
    )
    return SearchResponse(results=results, total=len(results))


@router.get("/products/{product_id}/similar", response_model=SearchResponse)
async def similar_products(
    product_id: str,
    top_k: int = Query(10, ge=1, le=100)
):
    """获取相似产品推荐"""
    results = get_recommendations(product_id, top_k=top_k)
    return SearchResponse(results=results, total=len(results))


@router.get("/stats", response_model=StatsResponse)
async def search_stats():
    """向量数据库统计信息"""
    total = get_total_count()
    return StatsResponse(
        total_products=total,
        message=f"向量数据库共有 {total} 条产品嵌入"
    )
