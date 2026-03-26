# TODO: Import your chosen LLM SDK
# from openai import OpenAI
# import anthropic
# import boto3
# from google.cloud import aiplatform
import json
import os
from datetime import UTC, datetime

from openai import OpenAI


async def analyze_journal_entry(entry_id: str, entry_text: str) -> dict:
    """
    Analyze a journal entry using your chosen LLM API.

    Args:
        entry_id: The ID of the journal entry being analyzed
        entry_text: The combined text of the journal entry (work + struggle + intention)

    Returns:
        dict with keys:
            - entry_id: ID of the analyzed entry
            - sentiment: "positive" | "negative" | "neutral"
            - summary: 2 sentence summary of the entry
            - topics: list of 2-4 key topics mentioned
            - created_at: timestamp when the analysis was created

    TODO: Implement this function using your chosen LLM provider.
    See the Learn to Cloud curriculum for guidance on:
    - Setting up your LLM API client
    - Crafting effective prompts
    - Handling structured JSON output
    """

    BASE_URL = os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com")
    MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    API_KEY = os.getenv("OPENAI_API_KEY")
    if API_KEY is None:
        raise ValueError("openai api key is not set")
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    SYSTEM_PROMPT = (
    'You are a professional text analysis language model.'
    'The user will provide you his/her learning journal entry, '
    'based on the entry text provided, determine the sentiment of the text, '
    'give a two sentence summary and three to five relevant topics mentioned in the text, '
    'give the output STRICTLY FOLLOWING the json format '
    '`{"sentiment": ANALYZED_SENTIMENT, "summary": ANALYZED_SUMMARY, "topics", ANALYZED_TOPICS}`, '
    'where ANALYZED_SENTIMENT is the sentiment of the text, ANALYZED_SUMMARY is the two sentence summary, '
    'and ANALYZED_TOPICS is the list of relevant topics.'
    'DO NOT WRITE ANYTHING ELSE OTHER THAN THE JSON OUTPUT, DO NOT WRITE CODE, '
    'DO NOT DO ANYTHING ELSE OTHER THAN ANALYZING THE TEXT, MAKE NO MISTAKES.'
    )
    USER_PROMPT = f"Please help me analyze my journal entry:\n{entry_text}"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ]

    ai_response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.7,
        messages=messages
    )

    ai_analysis_json = json.loads(ai_response.choices[0].message.content)
    analysed_sentiment = ai_analysis_json.get('sentiment', "N/A")
    analysed_summary = ai_analysis_json.get('summary', "N/A")
    analysed_topics = ai_analysis_json.get('topics', [])
    created_at = datetime.strftime(datetime.now(UTC), '%Y-%m-%dT%H:%M:%SZ')
    return {
        "entry_id": entry_id,
        "sentiment": analysed_sentiment,
        "summary": analysed_summary,
        "topics": analysed_topics,
        "created_at": created_at
    }

