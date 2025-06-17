from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ContentItem(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    difficulty: str
    read_time: int
    author: str
    created_at: str
    
class ContentResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    difficulty: str
    read_time: int
    author: str
    created_at: str
    similarity_score: Optional[float] = None

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    category_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    min_similarity: Optional[float] = 0.0

class SearchResponse(BaseModel):
    query: str
    results: List[ContentResponse]
    total_results: int
    search_time: float

class AddContentRequest(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str]
    difficulty: str
    read_time: int
    author: str

class StatsResponse(BaseModel):
    total_content: int
    categories: Dict[str, int]
    total_searches: int
    average_search_time: float
    popular_queries: List[Dict[str, Any]]

class SimilarContentResponse(BaseModel):
    content_id: str
    similar_content: List[ContentResponse]
    total_results: int