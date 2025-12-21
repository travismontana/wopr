import React, { useMemo, useState } from "react";
import "./css/theme.css";

type Subject = "setup" | "capture" | "move" | "thumbnail";

type StatusState =
  | { type: "ok" | "error" | "info"; message: string; path?: string }
  | null;

// nginx autoindex JSON entries look like: { "name": "...", "type": "file|directory", ... }
type NginxAutoIndexEntry = {
  name: string;
  type: "file" | "directory";
  mtime?: string;
  size?: number;
};

type PageSize = 20 | 50 | 100 | "all";

export default function ML() {
  // Capture dialog values (only shown in dialog)
  const [gameId, setGameId] = useState<string>("dune_imperium");
  const [subject, setSubject] = useState<Subject>("setup");
  const [subjectName, setSubjectName] = useState<string>("");
  const [sequence, setSequence] = useState<number>(1);

  // UI state
  const [status, setStatus] = useState<StatusState>(null);
  const [busy, setBusy] = useState<boolean>(false);

  const [showCaptureDialog, setShowCaptureDialog] = useState<boolean>(false);
  const [showGallery, setShowGallery] = useState<boolean>(false);

  // Image list (full list, client-side paginated)
  const [images, setImages] = useState<string[]>([]);
  const [loadingImages, setLoadingImages] = useState<boolean>(false);

  // Pagination controls
  const [pageSize, setPageSize] = useState<PageSize>(20);
  const [page, setPage] = useState<number>(1); // 1-based

  const canGo = useMemo(() => {
    const gidOk = gameId.trim().length > 0;
    const seqOk = Number.isFinite(sequence) && sequence >= 1;
    return gidOk && seqOk && !busy;
  }, [gameId, sequence, busy]);

  function toggleCaptureDialog() {
    if (busy) return;
    setStatus(null);
    setShowCaptureDialog((v) => !v);
  }

  const totalCount = images.length;

  const totalPages = useMemo(() => {
    if (pageSize === "all") return totalCount > 0 ? 1 : 0;
    return totalCount > 0 ? Math.ceil(totalCount / pageSize) : 0;
  }, [pageSize, totalCount]);

  const visibleImages = useMemo(() => {
    if (pageSize === "all") return images;

    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return images.slice(start, end);
  }, [images, page, pageSize]);

  function clampPage(newPage: number) {
    if (totalPages <= 0) return 1;
    if (newPage < 1) return 1;
    if (newPage > totalPages) return totalPages;
    return newPage;
  }

  async function toggleGallery() {
    if (showGallery) {
      setShowGallery(false);
      return;
    }

    const gid = gameId.trim();
    if (!gid) {
      setStatus({ type: "info", message: "Set game_id first (Capture panel)." });
      return;
    }

    setLoadingImages(true);
    setImages([]);
    setStatus(null);

    try {
      // nginx autoindex JSON listing of the directory
      // Include trailing slash so nginx treats it as a directory.
      const baseUrl = `/wopr/games/${encodeURIComponent(gid)}/`;

      const res = await fetch(baseUrl, {
        headers: { Accept: "application/json" },
      });

      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const entries = (await res.json()) as NginxAutoIndexEntry[];

      const exts = [".jpg", ".jpeg", ".png", ".webp"];
      const imgs = entries
        .filter((e) => e.type === "file")
        .map((e) => e.name)
        .filter((name) => exts.some((x) => name.toLowerCase().endsWith(x)))
        // Your filenames are YYYYMMDD-HHMMSS-... so string sort works.
        // If you want newest first, reverse after sort.
        .sort()
        .reverse()
        .map((name) => `${baseUrl}${encodeURIComponent(name)}`);

      setImages(imgs);
      setPage(1); // reset pagination when opening
      setShowGallery(true);
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to load images" });
    } finally {
      setLoadingImages(false);
    }
  }

  async function doCapture() {
    if (!canGo) {
      setStatus({ type: "info", message: "Fill in game_id and set sequence >= 1." });
      return;
    }

    setBusy(true);
    setStatus({ type: "info", message: "Capturing…" });

    try {
      const res = await fetch("/api/cam/capture_ml", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          game_id: gameId.trim(),
          subject,
          subject_name: subjectName.trim() || subject,
          sequence: Number(sequence),
        }),
      });

      const raw = (await res.text()).trim();
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${raw}`);

      const httpPath = raw.startsWith("/remote/wopr/")
        ? `/wopr/${raw.slice("/remote/wopr/".length)}`
        : raw;

      setStatus({ type: "ok", message: "Saved", path: httpPath });

      setSequence((s) => s + 1);
      setShowCaptureDialog(false);

      // Optional: if gallery is open, refresh list
      // Keeping simple for now: user can click View again.
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? String(e) });
    } finally {
      setBusy(false);
    }
  }

  function onChangePageSize(v: PageSize) {
    setPageSize(v);
    setPage(1); // reset to first page whenever size changes
  }

  const pageLabel = useMemo(() => {
    if (!showGallery) return "";
    if (totalCount === 0) return "0";
    if (pageSize === "all") return `${totalCount}`;
    const start = (page - 1) * pageSize + 1;
    const end = Math.min(page * pageSize, totalCount);
    return `${start}-${end} of ${totalCount}`;
  }, [showGallery, totalCount, page, pageSize]);

  return (
    <section className="camera-panel">
      <h1>ML Controls</h1>

      <div className="actions">
        <button onClick={toggleCaptureDialog} disabled={busy}>
          {showCaptureDialog ? "Close Capture" : "Capture"}
        </button>

        <button onClick={toggleGallery} disabled={busy || loadingImages}>
          {showGallery ? "Close View" : loadingImages ? "Loading…" : "View"}
        </button>
      </div>

      {status && (
        <div className={`status status-${status.type}`}>
          {status.message}
          {status.path && (
            <>
              :{" "}
              <a href={status.path} target="_blank" rel="noreferrer">
                {status.path}
              </a>
            </>
          )}
        </div>
      )}

      {/* Capture dialog */}
      {showCaptureDialog && (
        <div className="wopr-dialog-backdrop" role="dialog" aria-modal="true">
          <div className="wopr-dialog">
            <h2>Capture</h2>

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
                <select value={subject} onChange={(e) => setSubject(e.target.value as Subject)}>
                  <option value="setup">setup</option>
                  <option value="capture">capture</option>
                  <option value="move">move</option>
                  <option value="thumbnail">thumbnail</option>
                </select>
              </label>

              <label>
                Subject Name
                <input
                  type="text"
                  value={subjectName}
                  onChange={(e) => setSubjectName(e.target.value)}
                  placeholder="Enter subject name"
                />
              </label>

              <label>
                Subject
                <select value={subject} onChange={(e) => setSubject(e.target.value as Subject)}>
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

            <div className="wopr-dialog-actions">
              <button onClick={toggleCaptureDialog} disabled={busy}>
                Close
              </button>
              <button onClick={doCapture} disabled={!canGo}>
                {busy ? "Capturing…" : "Go"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Gallery */}
      {showGallery && (
        <section className="gallery-panel">
          <div className="gallery-header" style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
            <h2 style={{ margin: 0 }}>Images for {gameId.trim()}</h2>

            <div style={{ marginLeft: "auto", display: "flex", gap: "0.75rem", alignItems: "center" }}>
              <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                Show
                <select
                  value={pageSize}
                  onChange={(e) => {
                    const v = e.target.value;
                    const next: PageSize =
                      v === "20" ? 20 : v === "50" ? 50 : v === "100" ? 100 : "all";
                    onChangePageSize(next);
                  }}
                >
                  <option value="20">20</option>
                  <option value="50">50</option>
                  <option value="100">100</option>
                  <option value="all">all</option>
                </select>
              </label>

              <span style={{ opacity: 0.8, whiteSpace: "nowrap" }}>{pageLabel}</span>

              {pageSize !== "all" && totalPages > 1 && (
                <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                  <button
                    onClick={() => setPage((p) => clampPage(p - 1))}
                    disabled={page <= 1}
                  >
                    Prev
                  </button>
                  <span style={{ opacity: 0.85, whiteSpace: "nowrap" }}>
                    Page {page} / {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => clampPage(p + 1))}
                    disabled={page >= totalPages}
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          </div>

          {totalCount === 0 ? (
            <p>(No images found)</p>
          ) : (
            <ul className="gallery-links">
              {visibleImages.map((img) => (
                <li key={img}>
                  <a href={img} target="_blank" rel="noreferrer">
                    {decodeURIComponent(img.split("/").pop() || img)}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </section>
  );
}
