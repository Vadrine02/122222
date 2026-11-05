import { useState } from "react";
import { submitLocation } from "../api";

export default function GeoRequest({ onLocation }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function request() {
    setBusy(true); setError("");
    navigator.geolocation.getCurrentPosition(
      async ({ coords }) => {
        const loc = { lat: coords.latitude, lng: coords.longitude };
        try { await submitLocation(loc.lat, loc.lng); } catch { /* non-fatal: search still works */ }
        onLocation(loc);
      },
      (err) => {
        setBusy(false);
        setError(err.code === 1
          ? "Location access is blocked. Allow it in your device settings, then try again."
          : "Couldn't get your location. Check GPS or signal and try again.");
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  return (
    <main className="app center">
      <h1>Find the cheapest groceries near you</h1>
      <p className="muted">We search shops within 3 km of where you are.</p>
      <button className="primary" onClick={request} disabled={busy}>
        {busy ? "Locating…" : "Share my location"}
      </button>
      {error && <p className="error">{error}</p>}
    </main>
  );
}
