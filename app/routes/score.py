import logging

from fastapi import APIRouter, Query, HTTPException

import app.context as context
from app.services.llm import generate_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[score]")

router = APIRouter()


@router.get("/score")
def get_articles_by_score(
    threshold: float = Query(..., description="Relevance score threshold"),
    limit: int = Query(5, ge=1, le=20, description="Number of articles to return")
):
    try:
        logger.info(f"SCORE | Fetching articles with relevance score >= {threshold}")
        results = context.articles_collection.find(
            {"relevance_score": {"$gte": threshold}}
        ).sort("relevance_score", -1).limit(limit)

        articles = []
        for article in results:
            articles.append({
                "_id": str(article.get("_id")),
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "publication_date": article.get("publication_date"),
                "source_name": article.get("source_name"),
                "category": article.get("category"),
                "relevance_score": article.get("relevance_score"),
                "latitude": article.get("latitude"),
                "longitude": article.get("longitude"),
                "llm_summary": generate_summary(article.get("title", ""), article.get("description", ""))
            })
        logger.info(f"SCORE | Fetched {len(articles)} articles with relevance score >= {threshold}")

        return {"articles": articles}

    except Exception as e:
        logger.error(f"SCORE | Error fetching articles by score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching articles by score: {str(e)}")