import json
import logging
import os
import redis
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI
from groq import Groq
from pymongo import MongoClient

import app.context as context
from app.routes import (
    category, source, score, search, nearby,
    query, simulate, trending
)


class App:
    def __init__(self):
        self._app = FastAPI(
            title="Contextual News Retrieval",
            version="1.0",
            description="LLM-powered news retrieval backend",
            docs_url="/docs"
        )
        self._setup_logging()
        self._load_env()
        self._connect_to_mongo()
        self._connect_to_redis()
        self._init_llm_client()
        self._load_news_data_if_needed()
        self._register_routes()

    def _load_env(self):
        load_dotenv(dotenv_path="configs/.env")
        self.logger.info("[App] Loaded Environment Variables.")

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("NewsAPI")
        self.logger.info("[App] Setup Logger.")

    def _connect_to_mongo(self):
        mongo_uri = os.getenv("MONGO_URI")
        db_name = os.getenv("DB_NAME")

        try:
            self.client = MongoClient(mongo_uri)
            self.logger.info(f"[App] Connected to MongoDB at '{mongo_uri}{db_name}'")
        except Exception as e:
            self.logger.error(f"[App] Failed to connect to MongoDB: {str(e)}")
            raise

        self.db = self.client[db_name]
        self.articles_collection = self.db["articles"]
        context.db = self.db
        context.articles_collection = self.articles_collection
        context.user_events_collection = self.db["user_events"]

    def _connect_to_redis(self):
        redis_url = os.getenv("REDIS_URL")

        try:
            context.redis_client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
            self.logger.info(f"[App] Connected to Redis at '{redis_url}'")
        except Exception as e:
            self.logger.error(f"[App] Failed to connect to Redis: {str(e)}")
            raise

    def _init_llm_client(self):
        groq_api_key = os.getenv("GROQ_API_KEY")
        context.llm_client = Groq(api_key=groq_api_key)
        self.logger.info("[App] Initialized LLM client.")

    def _load_news_data_if_needed(self):
        self.logger.info("[App] Loading article data into MongoDB...")
        if self.articles_collection.count_documents({}) == 0:
            with open("data/news_data.json", "r", encoding="utf-8") as f:
                articles = json.load(f)

            for article in articles:
                if "publication_date" in article:
                    article["publication_date"] = datetime.fromisoformat(article["publication_date"])

            self.articles_collection.insert_many(articles)
            self.logger.info(f"[App] Inserted {len(articles)} articles into MongoDB.")

            # Create text index on title and description
            self.logger.info("[App] Creating text index on articles collection...")
            self.articles_collection.create_index(
                [("title", "text"), ("description", "text")],
                name="TextIndex"
            )
            self.logger.info("[App] Text index created successfully.")

        else:
            self.logger.info("[App] MongoDB already contains article data.")

    def _register_routes(self):
        self._app.include_router(category.router, prefix="/api/v1/news")
        self._app.include_router(source.router, prefix="/api/v1/news")
        self._app.include_router(score.router, prefix="/api/v1/news")
        self._app.include_router(search.router, prefix="/api/v1/news")
        self._app.include_router(nearby.router, prefix="/api/v1/news")
        self._app.include_router(query.router, prefix="/api/v1/news")
        self._app.include_router(simulate.router, prefix="/api/v1/news")
        self._app.include_router(trending.router, prefix="/api/v1/news")

    def get_app(self):
        return self._app