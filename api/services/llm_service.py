"""Task 4: Implement analyze_journal_entry using any OpenAI-compatible API.

This project mandates the OpenAI Python SDK, which works with:
  - GitHub Models (default, free, no credit card required)
  - OpenAI proper
  - Azure OpenAI
  - Groq, Together, OpenRouter, Fireworks, DeepInfra
  - Ollama, LM Studio, vLLM (local)
  - Anthropic via their OpenAI-compat endpoint

Set OPENAI_API_KEY, and optionally OPENAI_BASE_URL and OPENAI_MODEL
in your .env file. Settings are loaded by ``api.config.Settings``.
"""

import json
import os
from datetime import UTC, datetime

from openai import AsyncOpenAI

from api.config import get_settings


def _default_client() -> AsyncOpenAI:
    """Construct the real OpenAI client from application settings.

    Called lazily from ``analyze_journal_entry`` so tests can inject a
    ``MockAsyncOpenAI`` without ever triggering this code path.
    """
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )


async def analyze_journal_entry(
    entry_id: str,
    entry_text: str,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Analyze a journal entry using an OpenAI-compatible LLM.

    Args:
        entry_id: ID of the entry being analyzed (pass through to the result).
        entry_text: Combined work + struggle + intention text.
        client: OpenAI client. If None, a default one is constructed from
            application settings. Tests pass in a MockAsyncOpenAI here; production code
            in the router calls this with no ``client`` argument.

    Returns:
        dict with keys:
            - entry_id: ID of the analyzed entry
            - sentiment: "positive" | "negative" | "neutral"
            - summary: 2 sentence summary of the entry
            - topics: list of 2-4 key topics mentioned
            - created_at: timestamp when the analysis was created
    """

    base_url = os.getenv("OPENAI_BASE_URL", "https://models.inference.ai.azure.com")
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("openai api key is not set")
    if client is None:
        client = AsyncOpenAI(base_url=base_url, api_key=api_key)

    system_prompt = (
        "You are a professional text analysis language model."
        "The user will provide you his/her learning journal entry, "
        "based on the entry text provided, determine the sentiment of the text, "
        "give a two sentence summary and two to four relevant topics mentioned in the text, "
        "give the output STRICTLY FOLLOWING the json format "
        '`{"sentiment": ANALYZED_SENTIMENT, "summary": ANALYZED_SUMMARY, "topics", ANALYZED_TOPICS}`, '
        "where ANALYZED_SENTIMENT is the sentiment of the text and is restricted to be one of "
        "['positive', 'negative', 'uncertain'], ANALYZED_SUMMARY is the two sentence summary, "
        "and ANALYZED_TOPICS is the list of relevant topics."
        "DO NOT WRITE ANYTHING ELSE OTHER THAN THE JSON OUTPUT, DO NOT WRITE CODE, "
        "DO NOT DO ANYTHING ELSE OTHER THAN ANALYZING THE TEXT, MAKE NO MISTAKES."
    )
    user_prompt = f"Please help me analyze my journal entry:\n{entry_text}"

    ai_response = await client.chat.completions.create(
        model=model_name,
        temperature=0.7,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    ai_analysis_json = json.loads(ai_response.choices[0].message.content)
    analysed_sentiment = ai_analysis_json.get("sentiment", "N/A")
    analysed_summary = ai_analysis_json.get("summary", "N/A")
    analysed_topics = ai_analysis_json.get("topics", [])
    created_at = datetime.strftime(datetime.now(UTC), "%Y-%m-%dT%H:%M:%SZ")
    return {
        "entry_id": entry_id,
        "sentiment": analysed_sentiment,
        "summary": analysed_summary,
        "topics": analysed_topics,
        "created_at": created_at,
    }
