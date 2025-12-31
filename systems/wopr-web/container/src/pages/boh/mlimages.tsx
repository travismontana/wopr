import React, { useState, useEffect } from "react";

const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";

interface MLImage {
  id: number;
  uuid: string;  // NEW
  filename: string;
  object_rotation?: number;
  object_position?: string;
  color_temp?: string;
  light_intensity?: number;  // CHANGED: was string, now number
  game_uuid?: number;  // NEW (direct FK)
  piece_id?: number;  // NEW (direct FK)
  status: string;  // NEW
  user_created?: string;  // NEW
  date_created: string;  // was created_at
  user_updated?: string;  // NEW
  date_updated?: string;  // was updated_at
}

interface Game {
  id: number;
  name: string;
}

interface Piece {
  id: number;
  name: string;
}

interface MLImageFormData {
  object_rotation: string;
  object_position: string;
  color_temp: string;
  light_intensity: string;
  game_id: string;
  piece_id: string;
  locale: string;
}

type StatusState =
  | { type: "ok" | "error" | "info"; message: string }
  | null;

type SortField = "game" | "piece" | "filename" | "id";
type SortDirection = "asc" | "desc";

const ROTATION_OPTIONS = [0, 45, 90, 135, 180, 225, 270, 315];

const POSITION_OPTIONS = [
  { value: "center", label: "Center" },
  { value: "topLeft", label: "Top Left" },
  { value: "topRight", label: "Top Right" },
  { value: "bottomLeft", label: "Bottom Left" },
  { value: "bottomRight", label: "Bottom Right" },
  { value: "topEdge", label: "Top Edge" },
  { value: "bottomEdge", label: "Bottom Edge" },
  { value: "leftEdge", label: "Left Edge" },
  { value: "rightEdge", label: "Right Edge" },
  { value: "nearCenter", label: "Near Center" },
  { value: "random", label: "Random" },
];

const COLOR_TEMP_OPTIONS = ["neutral", "hot", "cold"];

const LIGHT_INTENSITY_OPTIONS = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10];

export default function MLImagesManager() {
  const [mlimages, setMLImages] = useState<MLImage[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusState>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingImage, setEditingImage] = useState<MLImage | null>(null);
  const [selectedGameFilter, setSelectedGameFilter] = useState<string>("");
  const [selectedPieceFilter, setSelectedPieceFilter] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>("id");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [formData, setFormData] = useState<MLImageFormData>({
    object_rotation: "0",
    object_position: "random",
    color_temp: "neutral",
    light_intensity: "70",
    game_id: "",
    piece_id: "",
    locale: "en",
  });

  useEffect(() => {
    console.log("[MLImagesManager] Component mounted, initializing data load");
    loadGames();
    loadPieces();
    loadMLImages();
  }, []);

  useEffect(() => {
    console.log("[MLImagesManager] Filters changed:", {
      gameFilter: selectedGameFilter,
      pieceFilter: selectedPieceFilter,
    });
    loadMLImages();
  }, [selectedGameFilter, selectedPieceFilter]);

  async function loadGames() {
    console.log("[loadGames] Fetching games from API");
    try {
      const res = await fetch(`${API_URL}/api/v1/games`);
      console.log("[loadGames] Response status:", res.status);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log("[loadGames] Loaded games:", data.length, "items");
      setGames(data);
    } catch (e: any) {
      console.error("[loadGames] Failed to load games:", e);
    }
  }

  async function loadPieces() {
    console.log("[loadPieces] Fetching pieces from API");
    try {
      const res = await fetch(`${API_URL}/api/v1/pieces`);
      console.log("[loadPieces] Response status:", res.status);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      console.log("[loadPieces] Loaded pieces:", data.length, "items");
      setPieces(data);
    } catch (e: any) {
      console.error("[loadPieces] Failed to load pieces:", e);
    }
  }

  async function loadMLImages() {
    console.log("[loadMLImages] Starting ML images load");
    setLoading(true);
    setStatus(null);

    try {
      const params = new URLSearchParams();
      if (selectedGameFilter) params.append("game_id", selectedGameFilter);
      if (selectedPieceFilter) params.append("piece_id", selectedPieceFilter);

      const queryString = params.toString();
      const url = queryString
        ? `${API_URL}/api/v1/mlimages?${queryString}`
        : `${API_URL}/api/v1/mlimages`;

      console.log("[loadMLImages] Fetching from URL:", url);
      const res = await fetch(url);
      console.log("[loadMLImages] Response status:", res.status);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      console.log("[loadMLImages] Loaded ML images:", data.length, "items");
      setMLImages(data);
    } catch (e: any) {
      console.error("[loadMLImages] Error loading ML images:", e);
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to load ML images",
      });
    } finally {
      setLoading(false);
    }
  }

  async function takePic(filename?: string) {
    console.log("[takePic] Capturing image with filename:", filename);
    const res = await fetch(`${API_URL}/api/v1/cameras/capture`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        captureType: "ml_capture",
        filename: filename.trim(),
      }),
    });
    console.log("[takePic] Capture response status:", res.status);
    if (!res.ok) {
      throw new Error(`Camera capture failed: HTTP ${res.status}`);
    }
    const result = await res.json();
    console.log("[takePic] Capture result:", result);
    return result;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    console.log("[handleSubmit] Form submitted", {
      isEdit: !!editingImage,
      formData,
    });
    setLoading(true);
    setStatus(null);

    try {
      const payload: any = {
        object_rotation: Number(formData.object_rotation),
        object_position: formData.object_position,
        color_temp: formData.color_temp,
        light_intensity: Number(formData.light_intensity),  // CHANGED: now number
        game_uuid: formData.game_id ? Number(formData.game_id) : undefined,  // CHANGED: direct FK
        piece_id: formData.piece_id ? Number(formData.piece_id) : undefined,  // CHANGED: direct FK
        status: "draft"  // NEW
      };

      // Only generate filename for new images, not edits
      if (!editingImage) {
        payload.filename = generateFilename();
        console.log("[handleSubmit] Generated filename:", payload.filename);
        await takePic(payload.filename);
      }

      const url = editingImage
        ? `${API_URL}/api/v1/mlimages/${editingImage.id}`
        : `${API_URL}/api/v1/mlimages`;

      const method = editingImage ? "PUT" : "POST";
      console.log("[handleSubmit] Sending request:", { method, url, payload });

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("[handleSubmit] Response status:", res.status);
      if (!res.ok) {
        const errorText = await res.text();
        console.error("[handleSubmit] Error response:", errorText);
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      const responseData = await res.json();
      console.log("[handleSubmit] Success response:", responseData);

      setStatus({
        type: "ok",
        message: editingImage ? "ML image updated!" : "ML image created!",
      });

      setFormData({
        object_rotation: "0",
        object_position: "random",
        color_temp: "neutral",
        light_intensity: "70",
        game_id: "",
        piece_id: "",
        locale: "en",
      });
      setEditingImage(null);
      setShowForm(false);
      await loadMLImages();
    } catch (e: any) {
      console.error("[handleSubmit] Failed to save ML image:", e);
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to save ML image",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(imageId: number, filename: string) {
    console.log("[handleDelete] Attempting to delete:", { imageId, filename });
    if (!confirm(`Delete ML image "${filename}"? This cannot be undone.`)) {
      console.log("[handleDelete] User cancelled deletion");
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      console.log("[handleDelete] Sending DELETE request for ID:", imageId);
      const res = await fetch(`${API_URL}/api/v1/mlimages/${imageId}`, {
        method: "DELETE",
      });

      console.log("[handleDelete] Response status:", res.status);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      console.log("[handleDelete] Successfully deleted:", filename);
      setStatus({ type: "ok", message: `Deleted "${filename}"` });
      await loadMLImages();
    } catch (e: any) {
      console.error("[handleDelete] Failed to delete ML image:", e);
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to delete ML image",
      });
    } finally {
      setLoading(false);
    }
  }

  function generateFilename(): string {
    console.log("[generateFilename] Generating filename with formData:", formData);
    const piece = pieces.find((p) => p.id === parseInt(formData.piece_id));
    const pieceName = piece?.name || "unknown";
    const game = games.find((g) => g.id === parseInt(formData.game_id));
    const gameName = game?.name || "unknown";
    console.log("[generateFilename] Resolved names:", { pieceName, gameName });

    const sanitize = (str: string): string => {
      return str
        .toLowerCase()
        .replace(/\s+/g, "_")
        .replace(/[^a-z0-9_-]/g, "_");
    };

    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    const timestamp = `${year}${month}${day}-${hours}${minutes}${seconds}`;

    const parts = [
      sanitize(pieceName),
      sanitize(gameName),
      sanitize(formData.object_position || "nopos"),
      `rot${formData.object_rotation || "0"}`,
      `pct${formData.light_intensity || "100"}`,
      `temp${sanitize(formData.color_temp || "neutral")}`,
      timestamp,
    ];

    const filename = `${parts.join("-")}.jpg`;
    console.log("[generateFilename] Generated filename:", filename);
    return filename;
  }

  function handleEdit(image: MLImage) {
    console.log("[handleEdit] Editing image:", image);
    setEditingImage(image);
    setFormData({
      object_rotation: image.object_rotation?.toString() || "",
      object_position: image.object_position || "",
      color_temp: image.color_temp || "",
      light_intensity: image.light_intensity?.toString() || "",
      game_id: image.game_id?.toString() || "",
      piece_id: image.piece_id?.toString() || "",
      locale: image.locale || "en",
    });
    setShowForm(true);
  }

  function handleCancel() {
    console.log("[handleCancel] Cancelling form");
    setShowForm(false);
    setEditingImage(null);
    setFormData({
      object_rotation: "0",
      object_position: "random",
      color_temp: "neutral",
      light_intensity: "70",
      game_id: "",
      piece_id: "",
      locale: "en",
    });
  }

  function handleSort(field: SortField) {
    console.log("[handleSort] Sort requested:", { field, currentField: sortField, currentDirection: sortDirection });
    if (sortField === field) {
      const newDirection = sortDirection === "asc" ? "desc" : "asc";
      console.log("[handleSort] Toggling direction to:", newDirection);
      setSortDirection(newDirection);
    } else {
      console.log("[handleSort] Changing sort field to:", field);
      setSortField(field);
      setSortDirection("asc");
    }
  }

  function getGameName(gameId?: number): string {
    console.log("[getGameName] Called with gameId:", gameId);
    if (!gameId) return "—";
    const game = games.find((g) => g.id === gameId);
    console.log("[getGameName] Found game:", game);
    return game?.name || `Game ${gameId}`;
  }

  function getPieceName(pieceId?: number): string {
    console.log("[getPieceName] Called with pieceId:", pieceId);
    if (!pieceId) return "—";
    const piece = pieces.find((p) => p.id === pieceId);
    console.log("[getPieceName] Found piece:", piece);
    return piece?.name || `Piece ${pieceId}`;
  }

  const sortedImages = [...mlimages].sort((a, b) => {
    let aVal: string | number;
    let bVal: string | number;

    switch (sortField) {
      case "game":
        aVal = getGameName(a.game_id);
        bVal = getGameName(b.game_id);
        break;
      case "piece":
        aVal = getPieceName(a.piece_id);
        bVal = getPieceName(b.piece_id);
        break;
      case "filename":
        aVal = a.filename || "";
        bVal = b.filename || "";
        break;
      case "id":
      default:
        aVal = a.id;
        bVal = b.id;
        break;
    }

    if (typeof aVal === "string" && typeof bVal === "string") {
      const comparison = aVal.localeCompare(bVal);
      return sortDirection === "asc" ? comparison : -comparison;
    }

    if (aVal < bVal) return sortDirection === "asc" ? -1 : 1;
    if (aVal > bVal) return sortDirection === "asc" ? 1 : -1;
    return 0;
  });

  console.log("[MLImagesManager] Render:", {
    mlimagesCount: mlimages.length,
    sortedImagesCount: sortedImages.length,
    gamesCount: games.length,
    piecesCount: pieces.length,
    loading,
    showForm,
    editingImage: !!editingImage,
  });

  return (
    <section className="panel">
      <h1>ML Images Management</h1>

      {/* Status Message */}
      {status && (
        <div className={`status-message ${status.type}`}>
          {status.message}
        </div>
      )}

      {/* Actions and Filters */}
      <div className="toolbar">
        <button onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add ML Image"}
        </button>
        <button onClick={loadMLImages} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>

        <label>
          Filter by Game:
          <select
            value={selectedGameFilter}
            onChange={(e) => setSelectedGameFilter(e.target.value)}
            disabled={loading}
          >
            <option value="">All</option>
            {games.map((game) => (
              <option key={game.id} value={game.id}>
                {game.name}
              </option>
            ))}
          </select>
        </label>

        <label>
          Filter by Piece:
          <select
            value={selectedPieceFilter}
            onChange={(e) => setSelectedPieceFilter(e.target.value)}
            disabled={loading}
          >
            <option value="">All</option>
            {pieces.map((piece) => (
              <option key={piece.id} value={piece.id}>
                {piece.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* Form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="form-container">
          <h3>{editingImage ? "Edit ML Image" : "New ML Image"}</h3>

          <div className="form-row">
            <div className="form-field">
              <label>Game *</label>
              <select
                value={formData.game_id}
                onChange={(e) =>
                  setFormData({ ...formData, game_id: e.target.value })
                }
                required
              >
                <option value="">Select a game...</option>
                {games.map((game) => (
                  <option key={game.id} value={game.id}>
                    {game.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Piece *</label>
              <select
                value={formData.piece_id}
                onChange={(e) =>
                  setFormData({ ...formData, piece_id: e.target.value })
                }
                required
              >
                <option value="">Select a piece...</option>
                {pieces.map((piece) => (
                  <option key={piece.id} value={piece.id}>
                    {piece.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Object Rotation</label>
              <select
                value={formData.object_rotation}
                onChange={(e) =>
                  setFormData({ ...formData, object_rotation: e.target.value })
                }
              >
                <option value="">Select rotation...</option>
                {ROTATION_OPTIONS.map((deg) => (
                  <option key={deg} value={deg}>
                    {deg}°
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Object Position</label>
              <select
                value={formData.object_position}
                onChange={(e) =>
                  setFormData({ ...formData, object_position: e.target.value })
                }
              >
                <option value="">Select position...</option>
                {POSITION_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Color Temperature</label>
              <select
                value={formData.color_temp}
                onChange={(e) =>
                  setFormData({ ...formData, color_temp: e.target.value })
                }
              >
                <option value="">Select color temp...</option>
                {COLOR_TEMP_OPTIONS.map((temp) => (
                  <option key={temp} value={temp}>
                    {temp}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Light Intensity</label>
              <select
                value={formData.light_intensity}
                onChange={(e) =>
                  setFormData({ ...formData, light_intensity: e.target.value })
                }
              >
                <option value="">Select intensity...</option>
                {LIGHT_INTENSITY_OPTIONS.map((intensity) => (
                  <option key={intensity} value={intensity}>
                    {intensity}%
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-field">
            <label>Locale</label>
            <input
              type="text"
              value={formData.locale}
              onChange={(e) =>
                setFormData({ ...formData, locale: e.target.value })
              }
              placeholder="en"
            />
          </div>

          <div className="actions">
            <button type="submit" disabled={loading}>
              {editingImage ? "Update" : "Create"}
            </button>
            <button type="button" onClick={handleCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* ML Images Table */}
      {loading && mlimages.length === 0 ? (
        <p>Loading ML images...</p>
      ) : mlimages.length === 0 ? (
        <p>No ML images found. Add one to get started.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort("game")}>
                Game {sortField === "game" && (sortDirection === "asc" ? "▲" : "▼")}
              </th>
              <th onClick={() => handleSort("piece")}>
                Piece {sortField === "piece" && (sortDirection === "asc" ? "▲" : "▼")}
              </th>
              <th onClick={() => handleSort("filename")}>
                Filename {sortField === "filename" && (sortDirection === "asc" ? "▲" : "▼")}
              </th>
              <th onClick={() => handleSort("id")}>
                ID {sortField === "id" && (sortDirection === "asc" ? "▲" : "▼")}
              </th>
              <th className="actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedImages.map((image) => (
              <tr key={image.id}>
                <td>{getGameName(image.game_id)}</td>
                <td>{getPieceName(image.piece_id)}</td>
                <td>{image.filename}</td>
                <td>{image.id}</td>
                <td className="actions">
                  <div className="action-buttons">
                    <button onClick={() => handleEdit(image)} disabled={loading}>
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(image.id, image.filename)}
                      disabled={loading}
                      className="danger"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}