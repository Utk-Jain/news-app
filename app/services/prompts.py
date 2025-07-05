SUMMARISE = """
You are a professional news summarizer.

Read the **title** and **description** below, and generate a clear, factual summary in **less than 60 words**. Ensure the summary captures the core news context using both title and description — no opinions, no repetition.

Title: {title}

Description: {description}

Summary:
"""

EXTRACT = """
You are an intelligent query analysis system. Given a user's natural language query, extract and return the following information as a valid JSON object.

Your job is to:
1. Identify the user's **intent(s)** from this fixed list:
   - "search": if the user is looking for specific news
   - "category": the category to which the user query belongs (e.g., politics, sports, business, technology, etc.)
   - "source": if a specific news source is mentioned (e.g., Reuters, Hindustan Times, News18, ET Now)
   - "nearby": if location or proximity is implied (e.g., "near me", "in Delhi")
   - "score": if relevance or quality is implied

2. Extract a flat list of **entities** from the query, combining important keywords, names, topics, and locations.

3. For the intents **"category"** and **"source"**, also extract their respective values.

Do NOT extract values for "search", "score", or "nearby".

### Output Format:
{{
  "intent": [...],
  "entities": [...],
  "values": {{
    "category": [...],   # if intent includes "category"
    "source": [...]      # if intent includes "source"
  }}
}}

User Query: "{query}"
"""