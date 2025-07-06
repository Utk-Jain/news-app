import logging
from collections import defaultdict
from datetime import datetime

from fastapi import APIRouter, Query, HTTPException

import app.context as context
from app.services.llm import generate_summary
from app.services.utils import haversine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[trending]")

router = APIRouter()


@router.get("/trending")
def get_trending_news(
    lat: float = Query(..., description="User's latitude"),
    lon: float = Query(..., description="User's longitude"),
    radius: float = Query(100, description="Radius in kilometers (default: 100km)"),
    limit: int = Query(5, ge=1, le=20, description="Number of trending articles to return")
):
    try:
        now = datetime.utcnow()
        trending_scores = defaultdict(lambda: 0)

        # Step 1: Get all user events within ~500km radius
        events = list(context.user_events_collection.find())

        for event in events:
            ev_lat = event["location"]["lat"]
            ev_lon = event["location"]["lon"]
            distance = haversine(lat, lon, ev_lat, ev_lon)

            if distance <= radius:
                time_diff = (now - event["timestamp"]).total_seconds() / 3600  # in hours
                decay = 1 / (time_diff + 1)
                base = 2 if event["event_type"] == "click" else 1
                proximity = 1 - (distance / radius)

                trending_scores[event["article_id"]] += base * decay * proximity

        # Step 2: Fetch articles and rank them
        article_ids = sorted(trending_scores, key=trending_scores.get, reverse=True)[:limit]
        articles = list(context.articles_collection.find({"id": {"$in": article_ids}}))

        # Step 3: Enrich and return
        results = []
        for article in articles:
            results.append({
                "_id": str(article.get("_id")),
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "publication_date": article["publication_date"],
                "source_name": article["source_name"],
                "category": article["category"],
                "relevance_score": article["relevance_score"],
                "latitude": article["latitude"],
                "longitude": article["longitude"],
                "llm_summary": generate_summary(article.get("title", ""), article.get("description", "")),
                "metadata": {
                    "trending_score": trending_scores[article["id"]],
                }
            })

        results.sort(key=lambda x: x["metadata"]["trending_score"], reverse=True)
        return {"trending_articles": results}

    except Exception as e:
        logger.error(f"TRENDING | Error generating trending articles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating trending articles: {str(e)}")