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
import { apiUrl } from "@lib/api";
const API_URL = apiUrl;

interface Piece {
  uuid: string;
  name: string;
  game_uuid: number;
  status: string;
  user_created?: string;
  date_created: string;
  user_updated?: string;
  date_updated?: string;
}

interface Game {
  id: number;
  name: string;
}

interface PieceFormData {
  name: string;
  description: string;
  locale: string;
  gameId: string;
}

// NEW: Bulk add state
interface BulkAddData {
  pieceNames: string;
  gameId: string;
}

type StatusState =
  | { type: "ok" | "error" | "info"; message: string }
  | null;

export default function PiecesManager() {
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusState>(null);
  const [showForm, setShowForm] = useState(false);
  const [showBulkForm, setShowBulkForm] = useState(false); // NEW
  const [editingPiece, setEditingPiece] = useState<Piece | null>(null);
  const [selectedGameFilter, setSelectedGameFilter] = useState<string>("");
  const [linkingPieceId, setLinkingPieceId] = useState<number | null>(null);
  const [formData, setFormData] = useState<PieceFormData>({
    name: "",
    description: "",
    locale: "en",
    gameId: "",
  });
  
  // NEW: Bulk add state
  const [bulkData, setBulkData] = useState<BulkAddData>({
    pieceNames: "",
    gameId: "",
  });

  useEffect(() => {
    loadGames();
    loadPieces();
  }, []);

  useEffect(() => {
    loadPieces();
  }, [selectedGameFilter]);

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
    setLoading(true);
    setStatus(null);

    try {
      const url = selectedGameFilter
        ? `${API_URL}/api/v1/pieces?game_id=${selectedGameFilter}`
        : `${API_URL}/api/v1/pieces`;

      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setPieces(data);
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to load pieces" });
    } finally {
      setLoading(false);
    }
  }

  // NEW: Bulk add handler
  async function handleBulkSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    const pieceList = bulkData.pieceNames
      .split('\n')
      .map(name => name.trim())
      .filter(name => name.length > 0);
    
    if (pieceList.length === 0) {
      setStatus({ type: "error", message: "No piece names provided" });
      return;
    }
    
    if (!bulkData.gameId) {
      setStatus({ type: "error", message: "Game selection required for bulk add" });
      return;
    }
    
    const gameName = games.find(g => g.id === Number(bulkData.gameId))?.name || "Unknown";
    
    if (!confirm(`Add ${pieceList.length} pieces to "${gameName}"?\n\n${pieceList.slice(0, 5).join('\n')}${pieceList.length > 5 ? '\n...' : ''}`)) {
      return;
    }
    
    setLoading(true);
    setStatus({ type: "info", message: `Adding ${pieceList.length} pieces...` });
    
    const results = {
      success: 0,
      failed: 0,
      errors: [] as string[]
    };
    
    for (const name of pieceList) {
      try {
        const payload = {
          name,
          game_uuid: Number(bulkData.gameId),
          status: "published"
        };
        
        const res = await fetch(`${API_URL}/api/v1/pieces`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        
        if (!res.ok) {
          const errorText = await res.text();
          throw new Error(`${name}: HTTP ${res.status}`);
        }
        
        results.success++;
      } catch (e: any) {
        results.failed++;
        results.errors.push(e?.message ?? `Failed: ${name}`);
      }
    }
    
    // Build status message
    let message = `Bulk add complete: ${results.success} added`;
    if (results.failed > 0) {
      message += `, ${results.failed} failed`;
      if (results.errors.length > 0) {
        message += `\n${results.errors.slice(0, 3).join('\n')}`;
        if (results.errors.length > 3) {
          message += `\n... and ${results.errors.length - 3} more`;
        }
      }
    }
    
    setStatus({
      type: results.failed > 0 ? "error" : "ok",
      message
    });
    
    setBulkData({ pieceNames: "", gameId: "" });
    setShowBulkForm(false);
    await loadPieces();
    setLoading(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setStatus(null);

    try {
      const payload = {
        name: formData.name.trim(),
        game_uuid: Number(formData.gameId),
        status: "published"
      };

      const url = editingPiece
        ? `${API_URL}/api/v1/pieces/${editingPiece.id}`
        : `${API_URL}/api/v1/pieces`;

      const method = editingPiece ? "PUT" : "POST";

      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      const savedPiece = await res.json();

      setStatus({
        type: "ok",
        message: editingPiece ? "Piece updated!" : "Piece created!",
      });

      setFormData({ name: "", description: "", locale: "en", gameId: "" });
      setEditingPiece(null);
      setShowForm(false);
      await loadPieces();
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to save piece" });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(pieceId: number, pieceName: string) {
    if (!confirm(`Delete piece "${pieceName}"? This cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/pieces/${pieceId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setStatus({ type: "ok", message: `Deleted "${pieceName}"` });
      await loadPieces();
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to delete piece" });
    } finally {
      setLoading(false);
    }
  }

  function handleEdit(piece: Piece) {
    setEditingPiece(piece);
    setFormData({
      name: piece.name || "",
      description: piece.description || "",
      locale: piece.locale || "en",
      gameId: "",
    });
    setShowForm(true);
  }

  function handleCancel() {
    setShowForm(false);
    setEditingPiece(null);
    setFormData({ name: "", description: "", locale: "en", gameId: "" });
  }
  
  // NEW: Bulk cancel
  function handleBulkCancel() {
    setShowBulkForm(false);
    setBulkData({ pieceNames: "", gameId: "" });
  }

  return (
    <section className="panel">
      <h1>Pieces Management</h1>

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
            whiteSpace: "pre-line", // NEW: Allow line breaks in status
          }}
        >
          {status.message}
        </div>
      )}

      {/* Actions */}
      <div className="actions" style={{ alignItems: "center" }}>
        <button onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add Piece"}
        </button>
        {/* NEW: Bulk add button */}
        <button 
          onClick={() => setShowBulkForm(!showBulkForm)} 
          disabled={loading}
          style={{ background: showBulkForm ? "#dc3545" : "#0dcaf0" }}
        >
          {showBulkForm ? "Cancel Bulk" : "Bulk Add"}
        </button>
        <button onClick={loadPieces} disabled={loading}>
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
            <option value="">All Pieces</option>
            {games.map((game) => (
              <option key={game.id} value={game.id}>
                {game.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {/* NEW: Bulk Add Form */}
      {showBulkForm && (
        <form
          onSubmit={handleBulkSubmit}
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "0.75rem",
            padding: "1rem",
            background: "#111",
            borderRadius: "8px",
            marginTop: "1rem",
            border: "1px solid #0dcaf0",
          }}
        >
          <h3 style={{ margin: 0 }}>Bulk Add Pieces</h3>
          
          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Game * (all pieces will be assigned to this game)
            </label>
            <select
              value={bulkData.gameId}
              onChange={(e) => setBulkData({ ...bulkData, gameId: e.target.value })}
              required
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
              }}
            >
              <option value="">-- Select a game --</option>
              {games.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Piece Names * (one per line)
            </label>
            <textarea
              value={bulkData.pieceNames}
              onChange={(e) => setBulkData({ ...bulkData, pieceNames: e.target.value })}
              required
              rows={10}
              placeholder="House Atreides&#10;House Harkonnen&#10;Fremen&#10;..."
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
                fontFamily: "monospace",
              }}
            />
            <p style={{ fontSize: "0.85em", color: "#aaa", marginTop: "0.25rem" }}>
              {bulkData.pieceNames.split('\n').filter(n => n.trim()).length} pieces to add
            </p>
          </div>

          <div className="actions" style={{ marginTop: "0.5rem" }}>
            <button type="submit" disabled={loading}>
              Add All
            </button>
            <button type="button" onClick={handleBulkCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

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
            {editingPiece ? "Edit Piece" : "New Piece"}
          </h3>

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
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

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={3}
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
              }}
            />
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

          <div>
            <label style={{ display: "block", marginBottom: "0.25rem" }}>
              Link to Game (optional)
            </label>
            <select
              value={formData.gameId}
              onChange={(e) =>
                setFormData({ ...formData, gameId: e.target.value })
              }
              style={{
                width: "100%",
                padding: "0.5rem",
                borderRadius: "4px",
                border: "1px solid #444",
              }}
            >
              <option value="">-- Select a game --</option>
              {games.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
            {games.length === 0 && (
              <p style={{ fontSize: "0.85em", color: "#aaa", marginTop: "0.25rem" }}>
                No games available.{" "}
                <a href="/games" style={{ color: "#0dcaf0" }}>
                  Add a game first
                </a>
              </p>
            )}
          </div>

          <div className="actions" style={{ marginTop: "0.5rem" }}>
            <button type="submit" disabled={loading}>
              {editingPiece ? "Update" : "Create"}
            </button>
            <button type="button" onClick={handleCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Pieces List */}
      <div style={{ marginTop: "1rem" }}>
        {loading && pieces.length === 0 ? (
          <p>Loading pieces...</p>
        ) : pieces.length === 0 ? (
          <p>
            {selectedGameFilter
              ? "No pieces found for this game."
              : "No pieces found. Add one to get started."}
          </p>
        ) : (
          <div
            style={{
              display: "grid",
              gap: "0.75rem",
              gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            }}
          >
            {pieces.map((piece) => (
              <div
                key={piece.id}
                style={{
                  padding: "1rem",
                  background: "#111",
                  borderRadius: "8px",
                  border: "1px solid #2222D6",
                }}
              >
                <h3 style={{ margin: "0 0 0.5rem 0" }}>{piece.name}</h3>
                {piece.description && (
                  <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.9em" }}>
                    {piece.description}
                  </p>
                )}
                <div style={{ fontSize: "0.85em", color: "#aaa" }}>
                  {piece.locale && <div>Locale: {piece.locale}</div>}
                  <div>ID: {piece.id}</div>
                </div>

                {/* Inline game linking section */}
                {linkingPieceId === piece.id ? (
                  <div
                    style={{
                      marginTop: "0.75rem",
                      padding: "0.75rem",
                      background: "#0a0a0a",
                      borderRadius: "4px",
                    }}
                  >
                    <label
                      style={{
                        display: "block",
                        marginBottom: "0.5rem",
                        fontSize: "0.9em",
                      }}
                    >
                      Select game to link:
                    </label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleLinkToGame(piece.id, Number(e.target.value));
                        }
                      }}
                      disabled={loading}
                      style={{
                        width: "100%",
                        padding: "0.5rem",
                        borderRadius: "4px",
                        border: "1px solid #444",
                        marginBottom: "0.5rem",
                      }}
                    >
                      <option value="">-- Choose a game --</option>
                      {games.map((game) => (
                        <option key={game.id} value={game.id}>
                          {game.name}
                        </option>
                      ))}
                    </select>
                    {games.length === 0 && (
                      <p style={{ fontSize: "0.85em", color: "#aaa", margin: "0 0 0.5rem 0" }}>
                        No games available.{" "}
                        <a href="/games" style={{ color: "#0dcaf0" }}>
                          Add one here
                        </a>
                      </p>
                    )}
                    <button
                      onClick={() => setLinkingPieceId(null)}
                      disabled={loading}
                      style={{ fontSize: "0.85em" }}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div
                    className="actions"
                    style={{ marginTop: "0.75rem", justifyContent: "flex-start" }}
                  >
                    <button onClick={() => handleEdit(piece)} disabled={loading}>
                      Edit
                    </button>
                    <button
                      onClick={() => setLinkingPieceId(piece.id)}
                      disabled={loading}
                      style={{ background: "#0dcaf0" }}
                    >
                      Link to Game
                    </button>
                    <button
                      onClick={() => handleDelete(piece.id, piece.name)}
                      disabled={loading}
                      style={{ background: "#dc3545" }}
                    >
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}