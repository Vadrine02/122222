import { useState } from "react";

export default function SearchBar({ onSearch, disabled }) {
  const [q, setQ] = useState("");
  const submit = (e) => { e.preventDefault(); if (q.trim().length >= 2) onSearch(q.trim()); };
  return (
    <div className="search">
      <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Milk, eggs, bread…"
             aria-label="Search products" enterKeyHint="search"
             onKeyDown={(e) => e.key === "Enter" && submit(e)} />
      <button className="primary" onClick={submit} disabled={disabled}>Search</button>
    </div>
  );
}
