"""Scraper skeleton. Subclass BaseScraper per chain, implement fetch_items()."""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx
from .. import db

log = logging.getLogger("scraper")

@dataclass
class ScrapedItem:
    external_id: str
    name: str
    unit: str | None
    price: float
    store_name: str          # must match stores.name for this chain

class BaseScraper(ABC):
    chain: str

    @abstractmethod
    async def fetch_items(self, http: httpx.AsyncClient) -> list[ScrapedItem]: ...

    async def run(self):
        async with httpx.AsyncClient(timeout=30, headers={"User-Agent": "GroceryTMA/1.0"}) as http:
            items = await self.fetch_items(http)
        async with db.pool.acquire() as conn, conn.transaction():
            for it in items:
                store_id = await conn.fetchval(
                    "SELECT id FROM stores WHERE chain=$1 AND name=$2", self.chain, it.store_name)
                if not store_id:
                    continue
                pid = await conn.fetchval(
                    """INSERT INTO products (name, unit, external_id) VALUES ($1,$2,$3)
                       ON CONFLICT (name, unit) DO UPDATE SET external_id = EXCLUDED.external_id
                       RETURNING id""", it.name, it.unit, it.external_id)
                await conn.execute(
                    "INSERT INTO prices_history (product_id, store_id, price) VALUES ($1,$2,$3)",
                    pid, store_id, it.price)
        log.info("%s: stored %d prices", self.chain, len(items))
