/**
 * Copyright 2026 Bob Bomar
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { useState, useEffect } from "react";
import "./css/theme.css";

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
  light_intensity?: string;
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
  filename: string;
  object_rotation: string;
  object_position: string;
  color_temp: string;
  light_intensity: string;
  locale: string;
}

type StatusState =
  | { type: "ok" | "error" | "info"; message: string }
  | null;

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
  const [formData, setFormData] = useState<MLImageFormData>({
    filename: "",
    object_rotation: "",
    object_position: "",
    color_temp: "",
    light_intensity: "",
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
      const payload = {
        filename: formData.filename.trim(),
        object_rotation: formData.object_rotation
          ? parseInt(formData.object_rotation)
          : undefined,
        object_position: formData.object_position.trim() || undefined,
        color_temp: formData.color_temp.trim() || undefined,
        light_intensity: formData.light_intensity.trim() || undefined,
        locale: formData.locale.trim() || undefined,
      };

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

  async function handleLinkToGame(imageId: number, gameId: number) {
    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(
        `${API_URL}/api/v1/mlimages/${imageId}/games/${gameId}`,
        { method: "POST" }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      setStatus({ type: "ok", message: "ML image linked to game!" });
      await loadMLImages();
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to link ML image to game",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handleLinkToPiece(imageId: number, pieceId: number) {
    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(
        `${API_URL}/api/v1/mlimages/${imageId}/pieces/${pieceId}`,
        { method: "POST" }
      );

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      setStatus({ type: "ok", message: "ML image linked to piece!" });
      await loadMLImages();
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to link ML image to piece",
      });
    } finally {
      setLoading(false);
    }
  }

  function handleEdit(image: MLImage) {
    setEditingImage(image);
    setFormData({
      filename: image.filename || "",
      object_rotation: image.object_rotation?.toString() || "",
      object_position: image.object_position || "",
      color_temp: image.color_temp || "",
      light_intensity: image.light_intensity || "",
      locale: image.locale || "en",
    });
    setShowForm(true);
  }

  function handleCancel() {
    setShowForm(false);
    setEditingImage(null);
    setFormData({
      filename: "",
      object_rotation: "",
      object_position: "",
      color_temp: "",
      light_intensity: "",
      locale: "en",
    });
  }

  function handleLinkToGameClick(imageId: number) {
    const gameId = prompt("Enter Game ID to link to:");
    if (gameId && !isNaN(Number(gameId))) {
      handleLinkToGame(imageId, Number(gameId));
    }
  }

  function handleLinkToPieceClick(imageId: number) {
    const pieceId = prompt("Enter Piece ID to link to:");
    if (pieceId && !isNaN(Number(pieceId))) {
      handleLinkToPiece(imageId, Number(pieceId));
    }
  }

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
          Game:
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
          Piece:
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

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Filename *
            </label>
            <input
              type="text"
              value={formData.filename}
              onChange={(e) =>
                setFormData({ ...formData, filename: e.target.value })
              }
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
              }}
            />
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Object Rotation (degrees)
              </label>
              <input
                type="number"
                min="0"
                max="360"
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
              />
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Object Position
              </label>
              <input
                type="text"
                value={formData.object_position}
                onChange={(e) =>
                  setFormData({ ...formData, object_position: e.target.value })
                }
                placeholder="center, top-left, etc."
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Color Temperature
              </label>
              <input
                type="text"
                value={formData.color_temp}
                onChange={(e) =>
                  setFormData({ ...formData, color_temp: e.target.value })
                }
                placeholder="5500K, warm, cool"
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              />
            </div>

            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Light Intensity
              </label>
              <input
                type="text"
                value={formData.light_intensity}
                onChange={(e) =>
                  setFormData({ ...formData, light_intensity: e.target.value })
                }
                placeholder="bright, dim, medium"
                style={{
                  width: "100%",
                  padding: "0.5rem",
                  borderRadius: "4px",
                  border: "1px solid #444",
                }}
              />
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

      {/* ML Images List */}
      <div style={{ marginTop: "1rem" }}>
        {loading && mlimages.length === 0 ? (
          <p>Loading ML images...</p>
        ) : mlimages.length === 0 ? (
          <p>No ML images found. Add one to get started.</p>
        ) : (
          <div
            style={{
              display: "grid",
              gap: "0.75rem",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
            }}
          >
            {mlimages.map((image) => (
              <div
                key={image.id}
                style={{
                  padding: "1rem",
                  background: "#111",
                  borderRadius: "8px",
                  border: "1px solid #2222D6",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 0.5rem 0",
                    wordBreak: "break-word",
                  }}
                >
                  {image.filename}
                </h3>

                <div style={{ fontSize: "0.85em", color: "#aaa" }}>
                  {image.object_rotation !== undefined && (
                    <div>Rotation: {image.object_rotation}°</div>
                  )}
                  {image.object_position && (
                    <div>Position: {image.object_position}</div>
                  )}
                  {image.color_temp && <div>Color: {image.color_temp}</div>}
                  {image.light_intensity && (
                    <div>Light: {image.light_intensity}</div>
                  )}
                  {image.locale && <div>Locale: {image.locale}</div>}
                  <div>ID: {image.id}</div>
                </div>

                <div
                  className="actions"
                  style={{
                    marginTop: "0.75rem",
                    justifyContent: "flex-start",
                    flexWrap: "wrap",
                  }}
                >
                  <button onClick={() => handleEdit(image)} disabled={loading}>
                    Edit
                  </button>
                  <button
                    onClick={() => handleLinkToGameClick(image.id)}
                    disabled={loading}
                    style={{ background: "#0dcaf0" }}
                  >
                    → Game
                  </button>
                  <button
                    onClick={() => handleLinkToPieceClick(image.id)}
                    disabled={loading}
                    style={{ background: "#198754" }}
                  >
                    → Piece
                  </button>
                  <button
                    onClick={() => handleDelete(image.id, image.filename)}
                    disabled={loading}
                    style={{ background: "#dc3545" }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
