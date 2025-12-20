import React, { useMemo, useState } from "react";
import "./css/theme.css";

type Subject = "setup" | "capture" | "move" | "thumbnail";

type StatusState =
  | { type: "ok" | "error" | "info"; message: string; path?: string }
  | null;

export default function Images() {
  const [gameId, setGameId] = useState<string>("dune_imperium");
  const [subject, setSubject] = useState<Subject>("setup");
  const [sequence, setSequence] = useState<number>(1);

  const [status, setStatus] = useState<StatusState>(null);
  const [busy, setBusy] = useState<boolean>(false);

  const canCapture = useMemo(() => {
    const gidOk = gameId.trim().length > 0;
    const seqOk = Number.isFinite(sequence) && sequence >= 1;
    return gidOk && seqOk && !busy;
  }, [gameId, sequence, busy]);

  async function handleCapture() {
    if (!canCapture) {
      setStatus({
        type: "info",
        message: "Fill in game_id and set sequence >= 1.",
      });
      return;
    }

    setBusy(true);
    setStatus({ type: "info", message: "Capturing…" });

    try {
      const res = await fetch("/api/cam/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_id: gameId.trim(),
          subject,
          sequence: Number(sequence),
        }),
      });

      const contentType = res.headers.get("content-type") || "";
      const raw = (await res.text()).trim();

      // Try to parse JSON errors (FastAPI 422, your 400 handler, etc.)
      let parsed: any = null;
      if (contentType.includes("application/json")) {
        try {
          parsed = JSON.parse(raw);
        } catch {
          // ignore JSON parse failures; fall back to raw
        }
      }

      if (!res.ok) {
        // FastAPI 422 shape: { detail: [ { msg, loc, ... } ] }
        const detailMsg =
          Array.isArray(parsed?.detail) && parsed.detail.length > 0
            ? parsed.detail.map((d: any) => d?.msg).filter(Boolean).join("; ")
            : null;

        const msg =
          parsed?.message ||
          parsed?.error ||
          detailMsg ||
          raw ||
          `HTTP ${res.status}`;

        throw new Error(`HTTP ${res.status}: ${msg}`);
      }

      // Success: server returns text path
      setStatus({
        type: "ok",
        message: "Saved",
        path: raw,
      });

      // Optional: auto-increment for next capture
      setSequence((s) => Number(s) + 1);
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? String(e),
      });
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="camera-panel">
      <h1>Camera Controls</h1>

      <div className="form">
        <label>
          Game ID
          <input
            type="text"
            value={gameId}
            onChange={(e) => setGameId(e.target.value)}
            placeholder="dune_imperium"
          />
        </label>

        <label>
          Subject
          <select
            value={subject}
            onChange={(e) => setSubject(e.target.value as Subject)}
          >
            <option value="setup">setup</option>
            <option value="capture">capture</option>
            <option value="move">move</option>
            <option value="thumbnail">thumbnail</option>
          </select>
        </label>

        <label>
          Sequence
          <input
            type="number"
            min={1}
            step={1}
            value={sequence}
            onChange={(e) => setSequence(Number(e.target.value))}
          />
        </label>
      </div>

      <div className="actions">
        <button onClick={handleCapture} disabled={!canCapture}>
          {busy ? "Capturing…" : "Capture"}
        </button>
        <button disabled>View</button>
        <button disabled>Confirm</button>
      </div>

      {status && (
        <div className={`status status-${status.type}`}>
          {status.message}
          {status.path && (
            <>
              :{" "}
              <a href={`file://${status.path}`} title={status.path}>
                {status.path}
              </a>
            </>
          )}
        </div>
      )}
    </section>
  );
}
