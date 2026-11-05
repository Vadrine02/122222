import { useEffect, useState } from "react";
import { initTelegram } from "./telegram";
import { searchProducts } from "./api";
import GeoRequest from "./components/GeoRequest";
import SearchBar from "./components/SearchBar";
import ProductList from "./components/ProductList";
import AiChat from "./components/AiChat";

export default function App() {
  const [loc, setLoc] = useState(null);
  const [tab, setTab] = useState("search");
  const [offers, setOffers] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(initTelegram, []);

  async function onSearch(q) {
    setLoading(true); setError("");
    try { setOffers(await searchProducts(q, loc)); }
    catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }

  if (!loc) return <GeoRequest onLocation={setLoc} />;

  return (
    <main className="app">
      <nav className="tabs" role="tablist">
        <button role="tab" aria-selected={tab === "search"} onClick={() => setTab("search")}>Prices</button>
        <button role="tab" aria-selected={tab === "ai"} onClick={() => setTab("ai")}>Recipe helper</button>
      </nav>
      {tab === "search" ? (
        <>
          <SearchBar onSearch={onSearch} disabled={loading} />
          {error && <p className="error">{error}</p>}
          <ProductList offers={offers} loading={loading} />
        </>
      ) : (
        <AiChat loc={loc} />
      )}
    </main>
  );
}
