import logging
import random
from datetime import datetime, timedelta

import app.context as context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[simulation_service]")


def simulate_user_events(num_events=500):
    logger.info(f"Simulating {num_events} user events...")
    articles = list(context.articles_collection.find())
    if not articles:
        return {"message": "No articles found. Load news data first."}

    context.user_events_collection.delete_many({})  # Reset existing events

    for _ in range(num_events):
        article = random.choice(articles)
        lat_jitter = random.uniform(-0.5, 0.5)
        lon_jitter = random.uniform(-0.5, 0.5)

        event = {
            "article_id": article["id"],
            "event_type": random.choice(["view", "click"]),
            "timestamp": datetime.utcnow() - timedelta(minutes=random.randint(0, 720)),  # up to 12 hrs ago
            "location": {
                "lat": article["latitude"] + lat_jitter,
                "lon": article["longitude"] + lon_jitter
            }
        }

        context.user_events_collection.insert_one(event)
    logger.info(f"Simulated {num_events} user events successfully.")

    return {"message": f"Simulated {num_events} user events."}