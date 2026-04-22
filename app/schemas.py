from typing import List, Optional

from pydantic import BaseModel


class CompareRequest(BaseModel):
    links: List[str]
    priority_mode: str = "balanced"
    category_mode: str = "auto"


class Recommendation(BaseModel):
    label: str
    score: str
    tone_class: str
    reason: str
    product_key: str


class Metric(BaseModel):
    label: str
    value: str
    note: str


class ProductResult(BaseModel):
    key: str
    brand: str
    name: str
    category: str
    price: int
    rating: float
    review_count: int
    summary: str
    pros: List[str]
    cons: List[str]
    specs: List[str]
    price_score: float
    quality_score: float
    value_score: float
    overall_score: float


class CompareResponse(BaseModel):
    status_message: str
    metrics: List[Metric]
    recommendations: List[Recommendation]
    products: List[ProductResult]
    error: Optional[str] = None
