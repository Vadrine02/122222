import { useRef, useEffect, useState } from "react";
import { chat } from "../api";
import { OfferRow } from "./ProductList";

export default function AiChat({ loc }) {
  const [msgs, setMsgs] = useState([{ role: "ai", reply: "Tell me what you want to cook and I'll build a shopping list with the cheapest nearby prices." }]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef();
  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [msgs]);

  async function send() {
    const message = text.trim();
    if (!message || busy) return;
    setMsgs((m) => [...m, { role: "user", reply: message }]);
    setText(""); setBusy(true);
    try {
      const r = await chat(message, loc);
      setMsgs((m) => [...m, { role: "ai", ...r }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "ai", reply: `Something went wrong: ${e.message}. Try again.` }]);
    } finally { setBusy(false); }
  }

  return (
    <section className="chat">
      <div className="log">
        {msgs.map((m, i) => (
          <div key={i} className={`bubble ${m.role}`}>
            <p>{m.reply}</p>
            {m.items?.length > 0 && (
              <>
                <ul className="offers">
                  {m.items.map((it, j) => it.offer
                    ? <OfferRow key={j} o={it.offer} />
                    : <li key={j} className="offer muted">{it.ingredient}: not found nearby</li>)}
                </ul>
                <p><strong>Estimated total: {m.total.toFixed(2)}</strong></p>
              </>
            )}
          </div>
        ))}
        {busy && <div className="bubble ai muted">Thinking…</div>}
        <div ref={end} />
      </div>
      <div className="search">
        <input value={text} onChange={(e) => setText(e.target.value)} placeholder="Dinner for 4 under 300…"
               aria-label="Message" onKeyDown={(e) => e.key === "Enter" && send()} />
        <button className="primary" onClick={send} disabled={busy}>Send</button>
      </div>
    </section>
  );
}
