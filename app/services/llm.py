import logging
from typing import List, Optional

from pydantic import BaseModel

import app.context as context
from app.services.prompts import SUMMARISE, EXTRACT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[llm]")


class ExtractionValues(BaseModel):
    category: Optional[List[str]] = []
    source: Optional[List[str]] = []


class LLMExtractionResult(BaseModel):
    entities: List[str]
    intent: List[str]
    values: ExtractionValues = ExtractionValues()


def generate_summary(title: str, description: str) -> str:
    try:
        prompt_template = SUMMARISE
        prompt = prompt_template.format(title=title, description=description)

        logger.info("Generating summary")
        chat_response = context.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256,
            stop=None,
            stream=False,
            response_format={"type": "text"},
        )
        logger.info("Summary generated successfully")

        return chat_response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return ""


def extract_entities_and_intent(query: str) -> dict:
    try:
        prompt_template = EXTRACT
        prompt = prompt_template.format(query=query)

        logger.info("Extracting entities and intent")
        chat_completion = context.llm_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=256,
            stop=None,
            stream=False,
            response_format={"type": "json_object"},
        )
        logger.info("Entities and intent extracted successfully")

        content = chat_completion.choices[0].message.content.strip()
        result = LLMExtractionResult.model_validate_json(content)
        return result.model_dump()

    except Exception as e:
        logger.error(f"Error extracting entities and intent: {e}")
        return {"entities": [], "intent": []}