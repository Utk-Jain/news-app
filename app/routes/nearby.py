import logging

from fastapi import APIRouter, Query, HTTPException

import app.context as context
from app.services.utils import haversine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[nearby]")

router = APIRouter()


@router.get("/nearby")
def get_articles_nearby(
    lat: float = Query(..., description="User latitude"),
    lon: float = Query(..., description="User longitude"),
    radius: float = Query(100, description="Radius in kilometers (default: 100km)"),
    limit: int = Query(5, ge=1, le=20, description="Number of articles to return")
):
    try:
        articles = []

        logger.info(f"NEARBY | Fetching articles within {radius} km radius of ({lat}, {lon})")
        for article in context.articles_collection.find():
            article_lat = article.get("latitude")
            article_lon = article.get("longitude")

            if article_lat is not None and article_lon is not None:
                distance = haversine(lat, lon, article_lat, article_lon)
                if distance <= radius:
                    article["distance"] = distance
                    articles.append(article)
        logger.info(f"NEARBY | Fetched {len(articles)} articles")

        # Sort by nearest distance
        articles = sorted(articles, key=lambda x: x["distance"])[:limit]

        response = []
        for article in articles:
            response.append({
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
                "llm_summary": ""
            })

        return {"articles": response}

    except Exception as e:
        logger.error(f"NEARBY | Error fetching nearby articles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching nearby articles: {str(e)}")