# 📰 Smart News Retrieval System

A smart backend system built using **FastAPI**, **MongoDB**, and **Groq LLM** that processes user queries, understands intent and location, and returns enriched news articles.

---

## 📦 Tech Stack

- Python 3.11
- FastAPI
- MongoDB (PyMongo)
- Groq (LLM API)
- Uvicorn
- Pydantic

---

## 🚀 Features

- ✅ LLM-powered entity and intent extraction
- ✅ Search articles by:
  - Category
  - Source
  - Text relevance
  - Relevance score
  - Location (nearby)
- ✅ Smart summarization and Entity extraction using LLM
- ✅ Unified `/query` endpoint for natural language search
- ✅ Pagination and metadata
- ✅ Error handling and logging

---

## 🔮 Future Improvements

While the current system is functional and LLM-integrated, several enhancements can significantly improve performance, scalability, and user experience:

### 1. 🔍 Integrate Elasticsearch for Advanced Search

MongoDB's text search is limited — it doesn't support fuzzy matching, custom ranking logic, or typo tolerance. Elasticsearch is built for fast, scalable, full-text search and ranking.
 
- Replace or augment `/search` and `/query` article fetching with Elasticsearch queries.
- Sync MongoDB articles to an Elasticsearch index.
- Use Elasticsearch’s scoring + full-text + proximity queries instead of `$regex` or `$text`.

### 2. 🧠 LLM Caching and Cost Optimization
- Cache summaries and intent-extraction responses using a hash of the query to avoid redundant LLM calls.

---

## 📂 Project Structure
```
inshorts-backend/
├── app/
│ ├── __init__.py
│ ├── context.py
│ ├── main.py
│ ├── routes/
│ │ ├── category.py
│ │ ├── nearby.py
│ │ ├── query.py
│ │ ├── score.py
│ │ ├── search.py
│ │ ├── simulate.py
│ │ ├── source.py
│ │ └── trending.py
│ ├── services/
│ │ ├── llm.py
│ │ ├── load_data.py
│ │ ├── prompts.py
│ │ ├── simulation.py
│ │ └── utils.py
├── configs/
│ └──  .env
├── data/
│ └── news_data.json
├── Makefile
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🔧 Setup Instructions
Ensure Python is installed on your system.

### 1. Clone, Set up Virtual env and Install Requirements

```bash
1. Clone:
    git clone <your_repo_url>
    cd inshorts-backend
    
2. Select a Python interpreter or create a virtual environment:
    python -m venv venv
    source venv/bin/activate   # For macOS/Linux
    # .\venv\Scripts\activate   # For Windows

3. Install dependencies:
    pip install -r requirements.txt
```


### 2. Set up Environment Variables
In configs/.env, setup your environment variables:
```bash
GROQ_API_KEY=your_api_key
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=news_db
REDIS_URL=redis://localhost:6379/0
```
Start MongoDB and Redis locally, if using local instances.
### 3. Run the Application
```bash
make run
```

### 4. Access the APIs
Open your browser and go to:
```
http://localhost:8000/docs
```
---

## 📘 Example API Requests
API: `/api/v1/news/query`
```bash
query="Top sports news from Hindustan Times near Mumbai"
lat=18.9582
lon=72.8321
page=1
limit=5

GET /api/v1/news/query?query=Top%20sports%20news%20from%20Hindustan%20Times%20near%20Mumbai&lat=18.9582&lon=72.8321&page=1&limit=5
```

API: `/api/v1/news/trending`
```bash
lat=18.9582
lon=72.8321
limit=5

GET /api/v1/news/trending?lat=18.9582&lon=72.8321&limit=5
```

API: `/api/v1/news/category`
```bash
value="sports"
limit=5

GET /api/v1/news/category?value=sports&limit=5
```

API: `/api/v1/news/source`
```bash
name="Reuters"
limit=5

GET /api/v1/news/source?name=Reuters&limit=5
```

API: `/api/v1/news/score`
```bash
threshold=0.7
limit=5

GET /api/v1/news/score?threshold=0.7&limit=5
```

API: `/api/v1/news/nearby`
```bash
lat=18.9582
lon=72.8321
limit=5

GET /api/v1/news/nearby?lat=18.9582&lon=72.8321&radius=100&limit=5
```

API: `/api/v1/news/search`
```bash
query="Top sports news from Hindustan Times near Mumbai"
limit=5

GET /api/v1/news/search?query=X%20owner%20elon%20musk%20and%20starlink&limit=5
```