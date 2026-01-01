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

      if (!res.ok