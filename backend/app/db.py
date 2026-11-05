import asyncpg
from .config import settings

pool: asyncpg.Pool | None = None

async def init_pool():
    global pool
    # statement_cache_size=0 is required behind Supabase/Neon pgbouncer pooling
    pool = await asyncpg.create_pool(settings.database_url, min_size=1, max_size=10,
                                     statement_cache_size=0)

async def close_pool():
    if pool:
        await pool.close()

NEARBY_SQL = """
SELECT p.id AS product_id, p.name, p.unit,
       s.id AS store_id, s.chain, s.name AS store_name,
       lp.price::float AS price, lp.currency, lp.scraped_at,
       ST_Distance(s.geom, pt.g) AS distance_m
FROM (SELECT ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography AS g) pt
JOIN stores s         ON ST_DWithin(s.geom, pt.g, $3)
JOIN latest_prices lp ON lp.store_id = s.id
JOIN products p       ON p.id = lp.product_id
WHERE p.name ILIKE '%' || $4 || '%' OR p.name % $4
ORDER BY lp.price ASC, distance_m ASC
LIMIT $5
"""

async def search_nearby(lat: float, lng: float, q: str, radius_m: int, limit: int = 30):
    rows = await pool.fetch(NEARBY_SQL, lng, lat, radius_m, q, limit)
    return [dict(r) for r in rows]
