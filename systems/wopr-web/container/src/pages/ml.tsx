import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

type Subject = "setup" | "capture" | "move" | "thumbnail";

type StatusState =
  | { type: "ok" | "error" | "info"; message: string; path?: string }
  | null;

type NginxAutoIndexEntry = {
  name: string;
  type: "file" | "directory";
  mtime?: string;
  size?: number;
};

type PageSize = 20 | 50 | 100 | "all";

export default function Images() {
  // Capture dialog values
  const [gameId, setGameId] = useState<string>("dune_imperium");
  const [subject, setSubject] = useState<Subject>("setup");
  const [subjectName, setSubjectName] = useState<string>("");
  const [sequence, setSequence] = useState<number>(1);

  // UI state
  const [status, setStatus] = useState<StatusState>(null);
  const [busy, setBusy] = useState<boolean>(false);

  const [showCaptureDialog, setShowCaptureDialog] = useState<boolean>(false);
  const [showGallery, setShowGallery] = useState<boolean>(false);

  // NEW: available games (dirs under /wopr/ml/)
  const [games, setGames] = useState<string[]>([]);
  const [loadingGames, setLoadingGames] = useState<boolean>(false);

  // Gallery state
  const [images, setImages] = useState<string[]>([]);
  const [loadingImages, setLoadingImages] = useState<boolean>(false);

  // Optional: subfolders inside selected game
  const [folders, setFolders] = useState<string[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>(""); // "" = root

  // Pagination
  const [pageSize, setPageSize] = useState<PageSize>(20);
  const [page, setPage] = useState<number>(1);

  const loadTokenRef = useRef<number>(0);

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

  function normalizeDirName(name: string) {
    return name.endsWith("/") ? name.slice(0, -1) : name;
  }

  // /wopr/ml/ -> list of game dirs
  async function loadGamesList() {
    const myToken = ++loadTokenRef.current;

    setLoadingGames(true);
    setStatus(null);

    try {
      const res = await fetch(`/wopr/ml/`, {
        headers: { Accept: "application/json" },
      });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const entries = (await res.json()) as NginxAutoIndexEntry[];

      if (myToken !== loadTokenRef.current) return;

      const dirs = entries
        .filter((e) => e.type === "directory")
        .map((e) => normalizeDirName(e.name))
        .filter((n) => n && n !== "." && n !== "..")
        .sort((a, b) => a.localeCompare(b));

      setGames(dirs);

      // If current gameId isn't valid, pick the first one
      if (dirs.length > 0 && !dirs.includes(gameId.trim())) {
        setGameId(dirs[0]);
      }
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to load game list" });
    } finally {
      if (myToken === loadTokenRef.current) setLoadingGames(false);
    }
  }

  function buildDirUrl(gid: string, folder: string) {
    const base = `/wopr/ml/${encodeURIComponent(gid)}/`;
    if (!folder) return base;
    return `${base}${encodeURIComponent(folder)}/`;
  }

  async function loadGallery(gid: string, folder: string) {
    const myToken = ++loadTokenRef.current;

    setLoadingImages(true);
    setStatus(null);
    setImages([]);

    try {
      const dirUrl = buildDirUrl(gid, folder);

      const res = await fetch(dirUrl, { headers: { Accept: "application/json" } });
      if (!res.ok) {
        const txt = await res.text();
        throw new Error(`HTTP ${res.status}: ${txt}`);
      }

      const entries = (await res.json()) as NginxAutoIndexEntry[];

      if (myToken !== loadTokenRef.current) return;

      // Populate subfolders from the game root listing only
      if (!folder) {
        const dirs = entries
          .filter((e) => e.type === "directory")
          .map((e) => normalizeDirName(e.name))
          .filter((n) => n && n !== "." && n !== "..")
          .sort((a, b) => a.localeCompare(b));

        setFolders(dirs);
      }

      const exts = [".jpg", ".jpeg", ".png", ".webp"];
      const imgs = entries
        .filter((e) => e.type === "file")
        .map((e) => e.name)
        .filter((name) => exts.some((x) => name.toLowerCase().endsWith(x)))
        .sort()
        .reverse()
        .map((name) => `${dirUrl}${encodeURIComponent(name)}`);

      setImages(imgs);
      setPage(1);
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to load images" });
    } finally {
      if (myToken === loadTokenRef.current) setLoadingImages(false);
    }
  }

  async function onGameChange(nextGameId: string) {
    setGameId(nextGameId);
    setSelectedFolder("");

    if (!showGallery) return;
    const gid = nextGameId.trim();
    if (!gid) return;

    await loadGallery(gid, "");
  }

  async function onFolderChange(nextFolder: string) {
    setSelectedFolder(nextFolder);

    if (!showGallery) return;
    const gid = gameId.trim();
    if (!gid) return;

    await loadGallery(gid, nextFolder);
  }

  async function toggleGallery() {
    if (showGallery) {
      setShowGallery(false);
      return;
    }

    const gid = gameId.trim();
    if (!gid) {
      setStatus({ type: "info", message: "Pick a game first." });
      return;
    }

    setShowGallery(true);
    setSelectedFolder("");
    await loadGallery(gid, "");
  }

  async function doCapture() {
    if (!canGo) {
      setStatus({ type: "info", message: "Fill in game_id and set sequence >= 1." });
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
          subject_name: subjectName.trim(),
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
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? String(e) });
    } finally {
      setBusy(false);
    }
  }

  function onChangePageSize(v: PageSize) {
    setPageSize(v);
    setPage(1);
  }

  const pageLabel = useMemo(() => {
    if (!showGallery) return "";
    if (totalCount === 0) return "0";
    if (pageSize === "all") return `${totalCount}`;
    const start = (page - 1) * pageSize + 1;
    const end = Math.min(page * pageSize, totalCount);
    return `${start}-${end} of ${totalCount}`;
  }, [showGallery, totalCount, page, pageSize]);

  // Load available games once
  useEffect(() => {
    loadGamesList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // If gameId changes while view is open (e.g., typing), reload root
  useEffect(() => {
    if (!showGallery) return;
    const gid = gameId.trim();
    if (!gid) return;
    setSelectedFolder("");
    loadGallery(gid, "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gameId, showGallery]);

  return (
    <section className="camera-panel">
      <h1>Machine Learning Controls</h1>

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
          <div
            className="gallery-header"
            style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}
          >
            <h2 style={{ margin: 0 }}>
              Images
              {gameId.trim() ? ` for ${gameId.trim()}` : ""}
              {selectedFolder ? ` / ${selectedFolder}` : ""}
            </h2>

            <div
              style={{
                marginLeft: "auto",
                display: "flex",
                gap: "0.75rem",
                alignItems: "center",
              }}
            >
              {/* Game selector from /wopr/ml/ */}
              <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                Game
                <select
                  value={gameId}
                  onChange={(e) => onGameChange(e.target.value)}
                  disabled={loadingGames || loadingImages}
                >
                  {games.length === 0 ? (
                    <option value={gameId}>{loadingGames ? "Loading…" : "(none found)"}</option>
                  ) : (
                    games.map((g) => (
                      <option key={g} value={g}>
                        {g}
                      </option>
                    ))
                  )}
                </select>
              </label>

              {/* Subfolder selector inside selected game */}
              <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                Folder
                <select
                  value={selectedFolder}
                  onChange={(e) => onFolderChange(e.target.value)}
                  disabled={loadingImages}
                >
                  <option value="">(root)</option>
                  {folders.map((f) => (
                    <option key={f} value={f}>
                      {f}
                    </option>
                  ))}
                </select>
              </label>

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
                  <button onClick={() => setPage((p) => clampPage(p - 1))} disabled={page <= 1}>
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
