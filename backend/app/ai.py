"""AI assistant: LLM plans the recipe + ingredients, DB prices them.
The LLM never invents prices -- it only returns ingredient names; we look them up."""
import json
from anthropic import AsyncAnthropic
from .config import settings
from . import db

client = AsyncAnthropic(api_key=settings.anthropic_api_key)

SYSTEM = """You are a grocery assistant. Reply ONLY with JSON:
{"reply": "<short friendly text, recipe steps if asked>",
 "ingredients": ["<generic grocery product search term>", ...]}
Use short, generic search terms (e.g. "milk", "chicken breast"). Max 15 ingredients.
Answer in the user's language."""

async def run_assistant(message: str, lat: float | None, lng: float | None) -> dict:
    resp = await client.messages.create(
        model=settings.anthropic_model, max_tokens=1200, system=SYSTEM,
        messages=[{"role": "user", "content": message}],
    )
    text = resp.content[0].text.strip().removeprefix("```json").removesuffix("```").strip()
    try:
        plan = json.loads(text)
    except json.JSONDecodeError:
        return {"reply": text, "items": [], "total": 0}

    items, total = [], 0.0
    for ing in plan.get("ingredients", []):
        offer = None
        if lat is not None and lng is not None:
            rows = await db.search_nearby(lat, lng, ing, settings.radius_m, limit=1)
            offer = rows[0] if rows else None
        if offer:
            total += offer["price"]
        items.append({"ingredient": ing, "offer": offer})
    return {"reply": plan.get("reply", ""), "items": items, "total": round(total, 2)}
