"""
Module: ai_service.py
Created: 2026-09-03
Purpose: Optional OpenAI-based enhancement of parsed CV data. Rule-based
         parsing always remains the fallback when AI is unavailable.
"""

import json

from app.config import settings
from app.schemas.resume import ParsedResumeData


def available() -> bool:
    """Return whether the AI service can be used.

    Returns:
        bool: True if an OpenAI API key is configured.
    """
    return bool(settings.openai_api_key)


async def enhance_parsed_data(data: ParsedResumeData) -> ParsedResumeData:
    """Optionally enrich parsed data via OpenAI, falling back to input.

    Async because it performs network I/O; callers await it. When OpenAI is
    not configured or the call fails, the original data is returned unchanged
    so rule-based parsing always works as a fallback.

    Args:
        data: Rule-based parsed resume data.

    Returns:
        ParsedResumeData: The AI-enhanced data, or the original on failure.
    """
    if not available():
        return data

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a resume structuring assistant. Given resume "
                        "JSON, return cleaned JSON of the SAME shape with polished "
                        "phrasing, but PRESERVE all factual content and meaning "
                        "exactly. Do not invent facts. Respond with JSON only."
                    ),
                },
                {"role": "user", "content": json.dumps(data.model_dump())},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        parsed = json.loads(content)
        return ParsedResumeData.model_validate(parsed)
    except Exception:
        return data
