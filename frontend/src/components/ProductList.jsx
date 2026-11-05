export const fmtDist = (m) => (m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(1)} km`);

export function OfferRow({ o }) {
  return (
    <li className="offer">
      <div>
        <strong>{o.name}</strong> {o.unit && <span className="muted">{o.unit}</span>}
        <div className="muted">{o.chain}, {o.store_name} · {fmtDist(o.distance_m)} away</div>
      </div>
      <div className="price">{o.price.toFixed(2)} {o.currency}</div>
    </li>
  );
}

export default function ProductList({ offers, loading }) {
  if (loading) return <p className="muted">Searching nearby shops…</p>;
  if (offers === null) return <p className="muted">Type a product to compare prices in your area.</p>;
  if (!offers.length) return <p className="muted">Nothing found within 3 km. Try a shorter or different name.</p>;
  return <ul className="offers">{offers.map((o) => <OfferRow key={`${o.product_id}-${o.store_id}`} o={o} />)}</ul>;
}
