import React, { useState, useEffect } from "react";

const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";

interface MLImage {
  id: number;
  document_id?: string;
  filename: string;
  uid?: string;
  create_time?: string;
  update_time?: string;
  object_rotation?: number;
  object_position?: string;
  color_temp?: string;
  light_intensity?: number;
  game_id?: number;
  piece_id?: number;
  created_at?: string;
  updated_at?: string;
  published_at?: string;
  created_by_id?: number;
  updated_by_id?: number;
  locale?: string;
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
    loadGames();
    loadPieces();
    loadMLImages();
  }, []);

  useEffect(() => {
    loadMLImages();
  }, [selectedGameFilter, selectedPieceFilter]);

  async function loadGames() {
    try {
      const res = await fetch(`${API_URL}/api/v1/games`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setGames(data);
    } catch (e: any) {
      console.error("Failed to load games:", e);
    }
  }

  async function loadPieces() {
    try {
      const res = await fetch(`${API_URL}/api/v1/pieces`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setPieces(data);
    } catch (e: any) {
      console.error("Failed to load pieces:", e);
    }
  }

  async function loadMLImages() {
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

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setMLImages(data);
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to load ML images",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      const payload: any = {
        object_rotation: formData.object_rotation
          ? parseInt(formData.object_rotation)
          : undefined,
        object_position: formData.object_position.trim() || undefined,
        color_temp: formData.color_temp.trim() || undefined,
        light_intensity: formData.light_intensity.trim() || undefined,
        game_id: parseInt(formData.game_id),
        piece_id: parseInt(formData.piece_id),
        locale: formData.locale.trim() || undefined,
      };

      // Only generate filename for new images, not edits
      if (!editingImage) {
        payload.filename = generateFilename();
      }
      const url = editingImage
        ? `${API_URL}/api/v1/mlimages/${editingImage.id}`
        : `${API_URL}/api/v1/mlimages`;

      const method = editingImage ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      setStatus({
        type: "ok",
        message: editingImage ? "ML image updated!" : "ML image created!",
      });

      setFormData({
        filename: "",
        object_rotation: "",
        object_position: "",
        color_temp: "",
        light_intensity: "",
        game_id: "",
        piece_id: "",
        locale: "en",
      });
      setEditingImage(null);
      setShowForm(false);
      await loadMLImages();
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to save ML image",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(imageId: number, filename: string) {
    if (!confirm(`Delete ML image "${filename}"? This cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/mlimages/${imageId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setStatus({ type: "ok", message: `Deleted "${filename}"` });
      await loadMLImages();
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to delete ML image",
      });
    } finally {
      setLoading(false);
    }
  }

  function generateFilename(): string {
    const piece = pieces.find((p) => p.id === parseInt(formData.piece_id));
    const pieceName = piece?.name || "unknown";
    
    const sanitize = (str: string): string => {
      return str
        .toLowerCase()
        .replace(/\s+/g, '_')
        .replace(/[^a-z0-9_-]/g, '_');
    };
    
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const timestamp = `${year}${month}${day}-${hours}${minutes}${seconds}`;
    
    const parts = [
      sanitize(pieceName),
      sanitize(formData.object_position || 'nopos'),
      `rot${formData.object_rotation || '0'}`,
      `pct${formData.light_intensity || '100'}`,
      `temp${sanitize(formData.color_temp || 'neutral')}`,
      timestamp
    ];
    
    return `${parts.join('-')}.jpg`;
  }

  function handleEdit(image: MLImage) {
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
    if (sortField === field) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  }

  function getGameName(gameId?: number): string {
    if (!gameId) return "—";
    const game = games.find((g) => g.id === gameId);
    return game?.name || `Game ${gameId}`;
  }

  function getPieceName(pieceId?: number): string {
    if (!pieceId) return "—";
    const piece = pieces.find((p) => p.id === pieceId);
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

  return (
    <section className="panel">
      <h1>ML Images Management</h1>

      {/* Status Message */}
      {status && (
        <div
          style={{
            padding: "0.75rem",
            borderRadius: "8px",
            background:
              status.type === "ok"
                ? "#198754"
                : status.type === "error"
                ? "#dc3545"
                : "#0dcaf0",
            color: "white",
            marginBottom: "1rem",
          }}
        >
          {status.message}
        </div>
      )}

      {/* Actions and Filters */}
      <div
        style={{
          display: "flex",
          gap: "0.75rem",
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <button onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add ML Image"}
        </button>
        <button onClick={loadMLImages} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>

        <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          Filter by Game:
          <select
            value={selectedGameFilter}
            onChange={(e) => setSelectedGameFilter(e.target.value)}
            disabled={loading}
            style={{
              padding: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #2222D6",
            }}
          >
            <option value="">All</option>
            {games.map((game) => (
              <option key={game.id} value={game.id}>
                {game.name}
              </option>
            ))}
          </select>
        </label>

        <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          Filter by Piece:
          <select
            value={selectedPieceFilter}
            onChange={(e) => setSelectedPieceFilter(e.target.value)}
            disabled={loading}
            style={{
              padding: "0.5rem",
              borderRadius: "4px",
              border: "1px solid #2222D6",
            }}
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
        <form
          onSubmit={handleSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
            padding: "1rem",
            background: "#111",
            borderRadius: "8px",
            marginTop: "1rem",
          }}
        >
          <h3 style={{ margin: 0 }}>
            {editingImage ? "Edit ML Image" : "New ML Image"}
          </h3>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Game *
              </label>
              <select
                value={formData.game_id}
                onChange={(e) =>
                  setFormData({ ...formData, game_id: e.target.value })
                }
                required
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              >
                <option value="">Select a game...</option>
                {games.map((game) => (
                  <option key={game.id} value={game.id}>
                    {game.name}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Piece *
              </label>
              <select
                value={formData.piece_id}
                onChange={(e) =>
                  setFormData({ ...formData, piece_id: e.target.value })
                }
                required
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
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

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Object Rotation
              </label>
              <select
                value={formData.object_rotation}
                onChange={(e) =>
                  setFormData({ ...formData, object_rotation: e.target.value })
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              >
                <option value="">Select rotation...</option>
                {ROTATION_OPTIONS.map((deg) => (
                  <option key={deg} value={deg}>
                    {deg}°
                  </option>
                ))}
              </select>
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Object Position
              </label>
              <select
                value={formData.object_position}
                onChange={(e) =>
                  setFormData({ ...formData, object_position: e.target.value })
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
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

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Color Temperature
              </label>
              <select
                value={formData.color_temp}
                onChange={(e) =>
                  setFormData({ ...formData, color_temp: e.target.value })
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              >
                <option value="">Select color temp...</option>
                {COLOR_TEMP_OPTIONS.map((temp) => (
                  <option key={temp} value={temp}>
                    {temp}
                  </option>
                ))}
              </select>
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Light Intensity
              </label>
              <select
                value={formData.light_intensity}
                onChange={(e) =>
                  setFormData({ ...formData, light_intensity: e.target.value })
                }
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
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

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Locale
            </label>
            <input
              type="text"
              value={formData.locale}
              onChange={(e) =>
                setFormData({ ...formData, locale: e.target.value })
              }
              placeholder="en"
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
              }}
            />
          </div>

          <div className="actions" style={{ marginTop: "0.5rem" }}>
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
      <div style={{ marginTop: "1rem", overflowX: "auto" }}>
        {loading && mlimages.length === 0 ? (
          <p>Loading ML images...</p>
        ) : mlimages.length === 0 ? (
          <p>No ML images found. Add one to get started.</p>
        ) : (
          <table
            style={{
              width: "100%",
              borderCollapse: "collapse",
              background: "#111",
              borderRadius: "8px",
            }}
          >
            <thead>
              <tr style={{ borderBottom: "2px solid #2222D6" }}>
                <th
                  onClick={() => handleSort("game")}
                  style={{
                    padding: "0.75rem",
                    textAlign: "left",
                    cursor: "pointer",
                    userSelect: "none",
                  }}
                >
                  Game{" "}
                  {sortField === "game" && (sortDirection === "asc" ? "▲" : "▼")}
                </th>
                <th
                  onClick={() => handleSort("piece")}
                  style={{
                    padding: "0.75rem",
                    textAlign: "left",
                    cursor: "pointer",
                    userSelect: "none",
                  }}
                >
                  Piece{" "}
                  {sortField === "piece" && (sortDirection === "asc" ? "▲" : "▼")}
                </th>
                <th
                  onClick={() => handleSort("filename")}
                  style={{
                    padding: "0.75rem",
                    textAlign: "left",
                    cursor: "pointer",
                    userSelect: "none",
                  }}
                >
                  Filename{" "}
                  {sortField === "filename" &&
                    (sortDirection === "asc" ? "▲" : "▼")}
                </th>
                <th
                  onClick={() => handleSort("id")}
                  style={{
                    padding: "0.75rem",
                    textAlign: "left",
                    cursor: "pointer",
                    userSelect: "none",
                  }}
                >
                  ID {sortField === "id" && (sortDirection === "asc" ? "▲" : "▼")}
                </th>
                <th
                  style={{
                    padding: "0.75rem",
                    textAlign: "right",
                  }}
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedImages.map((image) => (
                <tr
                  key={image.id}
                  style={{ borderBottom: "1px solid #333" }}
                >
                  <td style={{ padding: "0.75rem" }}>
                    {getGameName(image.game_id)}
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    {getPieceName(image.piece_id)}
                  </td>
                  <td style={{ padding: "0.75rem", wordBreak: "break-word" }}>
                    {image.filename}
                  </td>
                  <td style={{ padding: "0.75rem" }}>{image.id}</td>
                  <td style={{ padding: "0.75rem", textAlign: "right" }}>
                    <div
                      style={{
                        display: "flex",
                        gap: "0.5rem",
                        justifyContent: "flex-end",
                      }}
                    >
                      <button
                        onClick={() => handleEdit(image)}
                        disabled={loading}
                        style={{ padding: "0.25rem 0.5rem" }}
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(image.id, image.filename)}
                        disabled={loading}
                        style={{
                          padding: "0.25rem 0.5rem",
                          background: "#dc3545",
                        }}
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
      </div>
    </section>
  );
}