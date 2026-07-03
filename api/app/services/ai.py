import json
import httpx
from app.config import settings
from typing import Optional

REVIEW_SUMMARY_PROMPT = """You are analyzing reviews for a marketplace file.

File title: {title}
File category: {category}

Raw reviews (as JSON array):
{reviews_json}

Generate a structured summary as JSON with these EXACT keys:
- overall_sentiment: short 2-sentence summary of what users say
- strengths: array of 3 things it excels at (short phrases)
- weaknesses: array of 3 things to watch (short phrases)
- best_agent: which agent worked best, or "not enough data"
- use_case_fit: which domains it works for
- avg_time_to_results: typical time users reported
- pairing_insights: most commonly paired file types
- iteration_needed: "low", "medium", or "high"

CRITICAL RULE: Phrase weaknesses as researchable gaps, not dead-end criticisms.
BAD: "Does not work with streaming data"
GOOD: "Real-time streaming data handling can be improved — mitigation strategies exist"

Return ONLY valid JSON, no markdown, no other text.
"""


async def generate_review_summary(title: str, category: str, reviews: list[dict]) -> Optional[dict]:
    config = settings.active_ai_config
    api_key = config.get("api_key")
    if not api_key:
        return None

    prompt = REVIEW_SUMMARY_PROMPT.format(
        title=title,
        category=category.replace("_", " "),
        reviews_json=json.dumps(reviews, indent=2),
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if config["provider"] == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/washingtoneimae-dot/agent"
        headers["X-Title"] = "AgentMarket"

    payload = {
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 1000,
        "response_format": {"type": "json_object"},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{config['base_url']}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[-1]
                content = content.rsplit("\n```", 1)[0]
            return json.loads(content)
    except Exception as e:
        print(f"AI summary error: {e}")
        return None
