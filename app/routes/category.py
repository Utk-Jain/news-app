import logging

from fastapi import APIRouter, Query, HTTPException

import app.context as context
from app.services.llm import generate_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[category]")

router = APIRouter()


@router.get("/category")
def get_articles_by_category(
    value: list[str] = Query(..., description="News categories to filter articles by"),
    limit: int = Query(5, ge=1, le=20, description="Number of articles to return")
):
    try:
        category_values = [v.lower() for v in value]
        query = {
            "category": {
                "$elemMatch": {
                    "$regex": "|".join(category_values),
                    "$options": "i"
                }
            }
        }

        logger.info(f"CATEGORY | Fetching articles for category: {category_values}")
        results = context.articles_collection.find(
            query
        ).sort("publication_date", -1).limit(limit)

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
        logger.info(f"CATEGORY | Fetched {len(articles)} articles.")

        return {"articles": articles}

    except Exception as e:
        logger.error(f"CATEGORY | Error fetching articles by category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")