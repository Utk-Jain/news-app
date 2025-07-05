import logging

from fastapi import APIRouter, Query, HTTPException

import app.context as context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[search]")

router = APIRouter()


@router.get("/search")
def search_articles(
    query: str = Query(..., description="Search text in title and description"),
    limit: int = Query(5, ge=1, le=20, description="Number of articles to return")
):
    try:
        logger.info(f"Type of limit: {type(limit)}, Value: {limit}")

        # Filter: text search
        text_query = {
            "$text": {"$search": query}
        }
        projection = {
            "score": {"$meta": "textScore"},
            "title": 1,
            "description": 1,
            "url": 1,
            "publication_date": 1,
            "source_name": 1,
            "category": 1,
            "relevance_score": 1
        }

        logger.info(f"SEARCH | Searching articles with query: {query}")
        results = context.articles_collection.find(text_query, projection)

        articles = []
        for article in results:
            relevance = article.get("relevance_score", 0)
            text_score = article.get("score", 0)

            # Combine both
            final_score = 0.3 * relevance + 0.7 * text_score
            article["final_score"] = final_score

            articles.append(article)
        logger.info(f"SEARCH | Found {len(articles)} articles matching query: {query}")

        # Sort manually by combined score
        sorted_articles = sorted(articles, key=lambda x: x["final_score"], reverse=True)[:limit]

        # Format response
        response = []
        for article in sorted_articles:
            response.append({
                "_id": str(article.get("_id")),
                "title": article.get("title"),
                "description": article.get("description"),
                "url": article.get("url"),
                "publication_date": article.get("publication_date"),
                "source_name": article.get("source_name"),
                "category": article.get("category"),
                "relevance_score": round(article.get("relevance_score", 0), 2),
                "text_score": round(article.get("score", 0), 2),
                "final_score": round(article.get("final_score", 0), 2),
                "latitude": article.get("latitude"),
                "longitude": article.get("longitude"),
                "llm_summary": ""
            })

        return {"articles": response}

    except Exception as e:
        logger.error(f"SEARCH | Error during search: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error during search: {str(e)}")