"""Validate Telegram WebApp initData (HMAC-SHA256, per Telegram docs)."""
import hashlib, hmac, json
from urllib.parse import parse_qsl
from fastapi import Header, HTTPException
from .config import settings

def verify_init_data(init_data: str) -> dict:
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received = pairs.pop("hash", None)
    if not received:
        raise HTTPException(401, "Missing hash")
    check = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256).digest()
    calc = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc, received):
        raise HTTPException(401, "Bad initData signature")
    return json.loads(pairs["user"])

async def current_user(x_tg_init_data: str = Header(default="")) -> dict:
    if settings.skip_tg_auth:
        return {"id": 0}
    return verify_init_data(x_tg_init_data)
