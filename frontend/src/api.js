import { initData } from "./telegram";
const BASE = import.meta.env.VITE_API_URL;

async function req(path, opts = {}) {
  const res = await fetch(BASE + path, {
    ...opts,
    headers: { "Content-Type": "application/json", "X-TG-Init-Data": initData(), ...opts.headers },
  });
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.statusText);
  return res.status === 204 ? null : res.json();
}

export const submitLocation = (lat, lng) =>
  req("/api/location", { method: "POST", body: JSON.stringify({ lat, lng }) });
export const searchProducts = (q, { lat, lng }) =>
  req(`/api/products/search?q=${encodeURIComponent(q)}&lat=${lat}&lng=${lng}`);
export const chat = (message, loc) =>
  req("/api/assistant/chat", { method: "POST", body: JSON.stringify({ message, ...loc }) });
