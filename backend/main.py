from config.settings import settings
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from datetime import datetime
import logging

from .models import (
    SearchRequest, SearchResponse, ContentResponse,
    AddContentRequest, StatsResponse, SimilarContentResponse
)
from .database import db
from .langchain_integration import langchain_processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Content Recommender API",
    description="AI-powered content recommendation system using semantic search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    logger.info("Starting Content Recommender API...")
    try:
        db.load_sample_data()
        logger.info("API startup completed successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Content Recommender API",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/search", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """Search for content using semantic similarity with LangChain enhancement."""
    start_time = time.time()

    try:
        # Use LangChain for query expansion if available
        expanded_queries = langchain_processor.expand_query(request.query)
        logger.info(f"Query expanded to: {expanded_queries}")

        # Search with original query first, then expanded queries
        all_results = []
        seen_ids = set()

        for query in expanded_queries:
            results = db.search_content(
                query=query,
                max_results=request.max_results,
                category_filter=request.category_filter,
                difficulty_filter=request.difficulty_filter,
                min_similarity=request.min_similarity
            )

            # Add unique results
            for result in results:
                if result['id'] not in seen_ids:
                    all_results.append(result)
                    seen_ids.add(result['id'])

        # Sort by similarity score and limit results
        all_results.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        final_results = all_results[:request.max_results]

        # Enhance results with LangChain
        enhanced_results = langchain_processor.enhance_search_results(final_results, request.query)

        search_time = time.time() - start_time

        content_responses = [ContentResponse(**result) for result in enhanced_results]

        return SearchResponse(
            query=request.query,
            results=content_responses,
            total_results=len(content_responses),
            search_time=round(search_time, 4)
        )

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(content_id: str):
    """Get specific content by ID."""
    try:
        content = db.get_content_by_id(content_id)

        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return ContentResponse(**content)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@app.post("/add-content")
async def add_content(request: AddContentRequest):
    """Add new content to the database."""
    try:
        content_data = request.dict()
        content_id = db.add_content(content_data)

        return {
            "message": "Content added successfully",
            "content_id": content_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Add content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add content: {str(e)}")

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get database statistics and metrics."""
    try:
        stats = db.get_stats()
        return StatsResponse(**stats)

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/similar/{content_id}", response_model=SimilarContentResponse)
async def get_similar_content(content_id: str, max_results: int = 5):
    """Find content similar to a specific content item."""
    try:
        # Check if content exists
        original_content = db.get_content_by_id(content_id)
        if not original_content:
            raise HTTPException(status_code=404, detail="Content not found")

        similar_content = db.get_similar_content(content_id, max_results)
        content_responses = [ContentResponse(**content) for content in similar_content]

        return SimilarContentResponse(
            content_id=content_id,
            similar_content=content_responses,
            total_results=len(content_responses)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get similar content error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get similar content: {str(e)}")

@app.get("/query-suggestions/{query}")
async def get_query_suggestions(query: str):
    """Get search suggestions for a query."""
    try:
        # First perform a search to get context
        results = db.search_content(query, max_results=5)

        # Generate suggestions using LangChain
        suggestions = langchain_processor.generate_search_suggestions(query, results)

        # Analyze query intent
        intent_analysis = langchain_processor.analyze_search_intent(query)

        return {
            "query": query,
            "suggestions": suggestions,
            "intent_analysis": intent_analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Get suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@app.get("/health")
async def health_check():
    """Detailed health check with system status."""
    try:
        # Check database connection
        stats = db.get_stats()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": {
                "connected": True,
                "total_content": stats.get('total_content', 0)
            },
            "api": {
                "version": "1.0.0",
                "uptime": "running",
                "ai_provider": "Google Gemini"
            },
            "gemini": {
                "embeddings_enabled": settings.google_api_key is not None,
                "llm_enabled": langchain_processor.llm is not None,
                "embedding_model": settings.embedding_model,
                "llm_model": settings.llm_model
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

if __name__ == "__main__":
    import uvicorn
    from config.settings import settings

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    )