import React, { useEffect, useMemo, useRef, useState } from "react";
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

  // NEW: subdirectory selection for gallery
  const [folders, setFolders] = useState<string[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>(""); // "" = root

  // Pagination controls
  const [pageSize, setPageSize] = useState<PageSize>(20);
  const [page, setPage] = useState<number>(1); // 1-based

  // NEW: prevent stale fetch responses from overwriting newer ones
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

  // nginx autoindex directory entries often come as "name/" — normalize that
  function normalizeDirName(name: string) {
    return name.endsWith("/") ? name.slice(0, -1) : name;
  }

  // build the URL for the directory we are viewing (root or selected folder)
  function buildDirUrl(gid: string, folder: string) {
    const base = `/wopr/ml/${encodeURIComponent(gid)}/`;
    if (!folder) return base;
    return `${base}${encodeURIComponent(folder)}/`;
  }

  // loads folder list (from root only) + image list for a given folder
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

      // If this request is stale, ignore it
      if (myToken !== loadTokenRef.current) return;

      // Only populate folders from ROOT listing
      if (!folder) {
        const dirs = entries
          .filter((e) => e.type === "directory")
          .map((e) => normalizeDirName(e.name))
          .filter((n) => n && n !== ".." && n !== ".")
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
      // Only the newest request controls loading state
      if (myToken === loadTokenRef.current) setLoadingImages(false);
    }
  }

  async function onFolderChange(nextFolder: string) {
    const gid = gameId.trim();
    if (!gid) return;

    setSelectedFolder(nextFolder);
    await loadGallery(gid, nextFolder);
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

    setShowGallery(true);

    // Start from root when opening
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

      // Optional: if gallery is open, you can refresh.
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

  // OPTIONAL: if gameId changes while view is open, reload root + reset folder
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
      <h1>ML Controls</h1>

      <div className="actions">
        <button onClick={toggleCaptureDialog} disabled={busy}>
          {showCaptureDialog ? "Close Capture" : "Capture"}
        </button>

        <button onClick={toggleGallery} disabled={busy || loadingImages}>
          {showGallery ? "Close View" : loadingImages ? "Loading…" : "View"}
        </button>
      </d
