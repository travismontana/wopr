import React, { useState, useEffect } from "react";

const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";

interface Game {
  id: number;
  document_id?: string;
  uid?: string;
  name: string;
  description?: string;
  min_players?: number;
  max_players?: number;
  url?: string;  // NEW (BGG link)
  status: string;  // NEW ('draft' | 'published')
  user_created?: string;  // NEW (UUID)
  date_created: string;  // was created_at
  user_updated?: string;  // NEW (UUID)
  date_updated?: string;  // was updated_at
}

interface GameFormData {
  name: string;
  description: string;
  min_players: string;
  max_players: string;
  locale: string;
}

type StatusState =
  | { type: "ok" | "error" | "info"; message: string }
  | null;

export default function GamesManager() {
  const [games, setGames] = useState<Game[]>([]);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusState>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingGame, setEditingGame] = useState<Game | null>(null);
  const [formData, setFormData] = useState<GameFormData>({
    name: "",
    description: "",
    min_players: "",
    max_players: "",
    locale: "en",
  });

  useEffect(() => {
    loadGames();
  }, []);

  async function loadGames() {
    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/games`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setGames(data);
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to load games" });
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
        name: formData.name.trim(),
        description: formData.description.trim() || undefined,
        min_players: formData.min_players ? parseInt(formData.min_players) : undefined,
        max_players: formData.max_players ? parseInt(formData.max_players) : undefined,
        url: formData.url || undefined,  // NEW
        status: "published"  // NEW (or "published")
      };

      const url = editingGame
        ? `${API_URL}/api/v1/games/${editingGame.id}`
        : `${API_URL}/api/v1/games`;

      const method = editingGame ? "PUT" : "POST";

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
        message: editingGame ? "Game updated!" : "Game created!",
      });

      // Reset form and reload
      setFormData({
        name: "",
        description: "",
        min_players: "",
        max_players: "",
        locale: "en",
      });
      setEditingGame(null);
      setShowForm(false);
      await loadGames();
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to save game" });
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(gameId: number, gameName: string) {
    if (!confirm(`Delete game "${gameName}"? This cannot be undone.`)) {
      return;
    }

    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/games/${gameId}`, {
        method: "DELETE",
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      setStatus({ type: "ok", message: `Deleted "${gameName}"` });
      await loadGames();
    } catch (e: any) {
      setStatus({ type: "error", message: e?.message ?? "Failed to delete game" });
    } finally {
      setLoading(false);
    }
  }

  function handleEdit(game: Game) {
    setEditingGame(game);
    setFormData({
      name: game.name || "",
      description: game.description || "",
      min_players: game.min_players?.toString() || "",
      max_players: game.max_players?.toString() || "",
      locale: game.locale || "en",
    });
    setShowForm(true);
  }

  function handleCancel() {
    setShowForm(false);
    setEditingGame(null);
    setFormData({
      name: "",
      description: "",
      min_players: "",
      max_players: "",
      locale: "en",
    });
  }

  return (
    <section className="panel">
      <h1>Games Management</h1>

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

      {/* Actions */}
      <div className="actions">
        <button onClick={() => setShowForm(!showForm)} disabled={loading}>
          {showForm ? "Cancel" : "Add Game"}
        </button>
        <button onClick={loadGames} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>
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
            {editingGame ? "Edit Game" : "New Game"}
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

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: "block", marginBottom: "0.25rem" }}>
                Min Players
              </label>
              <input
                type="number"
                min="1"
                value={formData.min_players}
                onChange={(e) =>
                  setFormData({ ...formData, min_players: e.target.value })
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
                Max Players
              </label>
              <input
                type="number"
                min="1"
                value={formData.max_players}
                onChange={(e) =>
                  setFormData({ ...formData, max_players: e.target.value })
                }
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
              {editingGame ? "Update" : "Create"}
            </button>
            <button type="button" onClick={handleCancel} disabled={loading}>
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Games List */}
      <div style={{ marginTop: "1rem" }}>
        {loading && games.length === 0 ? (
          <p>Loading games...</p>
        ) : games.length === 0 ? (
          <p>No games found. Add one to get started.</p>
        ) : (
          <div
            style={{
              display: "grid",
              gap: "0.75rem",
              gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            }}
          >
            {games.map((game) => (
              <div
                key={game.id}
                style={{
                  padding: "1rem",
                  background: "#111",
                  borderRadius: "8px",
                  border: "1px solid #2222D6",
                }}
              >
                <h3 style={{ margin: "0 0 0.5rem 0" }}>{game.name}</h3>
                {game.description && (
                  <p style={{ margin: "0 0 0.5rem 0", fontSize: "0.9em" }}>
                    {game.description}
                  </p>
                )}
                <div style={{ fontSize: "0.85em", color: "#aaa" }}>
                  {game.min_players && game.max_players && (
                    <div>
                      Players: {game.min_players}-{game.max_players}
                    </div>
                  )}
                  {game.locale && <div>Locale: {game.locale}</div>}
                  <div>ID: {game.id}</div>
                </div>
                <div
                  className="actions"
                  style={{ marginTop: "0.75rem", justifyContent: "flex-start" }}
                >
                  <button
                    onClick={() => handleEdit(game)}
                    disabled={loading}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(game.id, game.name)}
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
