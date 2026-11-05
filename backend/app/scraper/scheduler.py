import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .example_chain import ExampleChainScraper

SCRAPERS = [ExampleChainScraper()]

async def _safe(s):
    try:
        await s.run()
    except Exception:
        logging.exception("scraper %s failed", s.chain)

def start() -> AsyncIOScheduler:
    sched = AsyncIOScheduler()
    for s in SCRAPERS:
        sched.add_job(_safe, "interval", hours=6, args=[s], id=s.chain)
    sched.start()
    return sched
