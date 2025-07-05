import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from app.routes.category import get_articles_by_category
from app.routes.nearby import get_articles_nearby
from app.routes.search import search_articles
from app.routes.source import get_articles_by_source
from app.services.llm import generate_summary, extract_entities_and_intent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[query]")

router = APIRouter()


@router.get("/query")
def smart_query(
    query: str = Query(..., description="Natural language query"),
    lat: Optional[float] = Query(None, description="User latitude (for nearby search)"),
    lon: Optional[float] = Query(None, description="User longitude (for nearby search)"),
    page: int = Query(1, ge=1),
    limit: int = Query(5, ge=1, le=20)
):
    try:
        # Extract entities and intent using LLM
        llm_result = extract_entities_and_intent(query)
        entities = llm_result.get("entities", [])
        intents = llm_result.get("intent", [])
        values = llm_result.get("values", {})

        logger.info(f"QUERY | LLM extracted entities: {entities}, intent: {intents}, values: {values}")

        results = []

        # 1. Intent: Search (title/description)
        if "search" in intents:
            search_terms = " ".join(entities)
            res = search_articles(query=search_terms, limit=limit)
            for a in res.get("articles", []):
                a["_source"] = "search"
                results.append(a)

        # 2. Intent: Category match
        if "category" in intents:
            category = values.get("category")
            res = get_articles_by_category(value=category, limit=limit)
            for a in res.get("articles", []):
                a["_source"] = "category"
                results.append(a)

        # 3. Intent: Source name
        if "source" in intents:
            source = values.get("source")
            res = get_articles_by_source(name=source, limit=limit)
            for a in res.get("articles", []):
                a["_source"] = "source"
                results.append(a)

        # 4. Intent: Nearby
        if "nearby" in intents and lat is not None and lon is not None:
            res = get_articles_nearby(
                lat=lat,
                lon=lon,
                radius=100,
                limit=limit
            )
            for a in res.get("articles", []):
                a["_source"] = "nearby"
                results.append(a)

        # Remove duplicates and sort by intent and relevance
        unique_articles = {str(a["_id"]): a for a in results}
        intent_priority = {
            "category": 1,
            "source": 1,
            "search": 2,
            "nearby": 3
        }
        sorted_articles = sorted(
            unique_articles.values(),
            key=lambda x: (
                intent_priority.get(x.get("_source"), 999),
                -x.get("relevance_score", 0)
            )
        )

        # Pagination
        start = (page - 1) * limit
        end = start + limit
        paginated_articles = sorted_articles[start:end]

        # Format response
        final_output = []
        for article in paginated_articles:
            final_output.append({
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

        logger.info(f"QUERY | Returning {len(final_output)} articles for query: '{query}'")

        return {
            "articles": final_output,
            "metadata": {
                "total_results": len(sorted_articles),
                "page": page,
                "limit": limit,
                "query": query
            }
        }

    except Exception as e:
        logger.error(f"QUERY | Error processing query '{query}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")