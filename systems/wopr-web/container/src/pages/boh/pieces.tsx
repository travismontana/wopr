import React, { useState, useEffect } from "react";

const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";

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
  const [showBulkForm, setShowBulkForm] = useState(false);
  const [editingPiece, setEditingPiece] = useState<Piece | null>(null);
  const [selectedGameFilter, setSelectedGameFilter] = useState<string>("");
  const [linkingPieceId, setLinkingPieceId] = useState<number | null>(null);
  const [formData, setFormData] = useState<PieceFormData>({
    name: "",
    description: "",
    locale: "en",
    gameId: "",
  });
  
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
  
  function handleBulkCancel() {
    setShowBulkForm(false);
    setBulkData({ pieceNames: "", gameId: "" });
  }

  return (
    <section className="panel">
      <h1>Pieces Management</h1>

      {status && (
        <div className={`status status-${status.type}`}>
          {status.message}
        </div>
      )}

      <div className="actions">
        <button onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add Piece"}
        </button>
        <button 
          className={showBulkForm ? "danger" : "info"}
          onClick={() => setShowBulkForm(!showBulkForm)} 
          disabled={loading}
        >
          {showBulkForm ? "Cancel Bulk" : "Bulk Add"}
        </button>
        <button onClick={loadPieces} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>

        <label className="filter-label">
          Filter by Game:
          <select
            value={selectedGameFilter}
            onChange={(e) => setSelectedGameFilter(e.target.value)}
            disabled={loading}
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

      {showBulkForm && (
        <form onSubmit={handleBulkSubmit} className="form-panel bulk-form">
          <h3>Bulk Add Pieces</h3>
          
          <div className="form-group">
            <label>
              Game * (all pieces will be assigned to this game)
            </label>
            <select
              value={bulkData.gameId}
              onChange={(e) => setBulkData({ ...bulkData, gameId: e.target.value })}
              required
            >
              <option value="">-- Select a game --</option>
              {games.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>
              Piece Names * (one per line)
            </label>
            <textarea
              className="bulk-textarea"
              value={bulkData.pieceNames}
              onChange={(e) => setBulkData({ ...bulkData, pieceNames: e.target.value })}
              required
              rows={10}
              placeholder="House Atreides&#10;House Harkonnen&#10;Fremen&#10;..."
            />
            <p className="hint">
              {bulkData.pieceNames.split('\n').filter(n => n.trim()).length} pieces to add
            </p>
          </div>

          <div className="actions">
            <button type="submit" disabled={loading}>
              Add All
            </button>
            <button type="button" onClick={handleBulkCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="form-panel">
          <h3>
            {editingPiece ? "Edit Piece" : "New Piece"}
          </h3>

          <div className="form-group">
            <label>Name *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              rows={3}
            />
          </div>

          <div className="form-group">
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

          <div className="form-group">
            <label>Link to Game (optional)</label>
            <select
              value={formData.gameId}
              onChange={(e) =>
                setFormData({ ...formData, gameId: e.target.value })
              }
            >
              <option value="">-- Select a game --</option>
              {games.map((game) => (
                <option key={game.id} value={game.id}>
                  {game.name}
                </option>
              ))}
            </select>
            {games.length === 0 && (
              <p className="hint">
                No games available.{" "}
                <a href="/games">Add a game first</a>
              </p>
            )}
          </div>

          <div className="actions">
            <button type="submit" disabled={loading}>
              {editingPiece ? "Update" : "Create"}
            </button>
            <button type="button" onClick={handleCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

      <div className="pieces-list">
        {loading && pieces.length === 0 ? (
          <p>Loading pieces...</p>
        ) : pieces.length === 0 ? (
          <p>
            {selectedGameFilter
              ? "No pieces found for this game."
              : "No pieces found. Add one to get started."}
          </p>
        ) : (
          <div className="pieces-grid">
            {pieces.map((piece) => (
              <div key={piece.id} className="piece-card">
                <h3>{piece.name}</h3>
                {piece.description && (
                  <p className="description">{piece.description}</p>
                )}
                <div className="metadata">
                  {piece.locale && <div>Locale: {piece.locale}</div>}
                  <div>ID: {piece.id}</div>
                </div>

                {linkingPieceId === piece.id ? (
                  <div className="link-section">
                    <label>Select game to link:</label>
                    <select
                      onChange={(e) => {
                        if (e.target.value) {
                          handleLinkToGame(piece.id, Number(e.target.value));
                        }
                      }}
                      disabled={loading}
                    >
                      <option value="">-- Choose a game --</option>
                      {games.map((game) => (
                        <option key={game.id} value={game.id}>
                          {game.name}
                        </option>
                      ))}
                    </select>
                    {games.length === 0 && (
                      <p className="hint">
                        No games available.{" "}
                        <a href="/games">Add one here</a>
                      </p>
                    )}
                    <button onClick={() => setLinkingPieceId(null)} disabled={loading}>
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="actions">
                    <button onClick={() => handleEdit(piece)} disabled={loading}>
                      Edit
                    </button>
                    <button
                      className="info"
                      onClick={() => setLinkingPieceId(piece.id)}
                      disabled={loading}
                    >
                      Link to Game
                    </button>
                    <button
                      className="danger"
                      onClick={() => handleDelete(piece.id, piece.name)}
                      disabled={loading}
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