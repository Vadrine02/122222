from bs4 import BeautifulSoup
from .base import BaseScraper, ScrapedItem

class ExampleChainScraper(BaseScraper):
    chain = "ExampleChain"
    URL = "https://example-chain.test/catalog?page={page}"   # TODO: real URL; respect robots.txt/ToS

    async def fetch_items(self, http):
        out = []
        for page in range(1, 4):
            html = (await http.get(self.URL.format(page=page))).text
            for card in BeautifulSoup(html, "html.parser").select(".product-card"):   # TODO selectors
                out.append(ScrapedItem(
                    external_id=card["data-sku"],
                    name=card.select_one(".title").get_text(strip=True),
                    unit=card.select_one(".unit").get_text(strip=True),
                    price=float(card.select_one(".price").get_text(strip=True).replace(",", ".")),
                    store_name="ExampleChain Central",
                ))
        return out
