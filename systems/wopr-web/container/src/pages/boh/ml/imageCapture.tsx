import { useState, useEffect } from 'react';

interface Game {
  id: number;
  name: string;
  uuid: string;
}

interface Piece {
  id: number;
  name: string;
  game_uuid: number;
  uuid: string;
}

interface ConfigData {
  object: {
    positions: string[];
    positionNames: string[];
    rotations: (string | number)[];
  };
  lightSettings: {
    intensity: string[];
    tempNames: string[];
    temps: {
      warm: string;
      neutral: string;
      cool: string;
    };
  };
}

interface CaptureFormData {
  game_id: number | null;
  piece_id: number | null;
  position_id: number;
  rotation: number;
  lighting_level: number;
  lighting_temp: string;
  notes: string;
}

const API_BASE = 'https://api.wopr.studio.abode.tailandtraillabs.org';

export default function MLImagesPage() {
  const [games, setGames] = useState<Game[]>([]);
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [formData, setFormData] = useState<CaptureFormData>({
    game_id: null,
    piece_id: null,
    position_id: 0,
    rotation: 0,
    lighting_level: 50,
    lighting_temp: 'neutral',
    notes: ''
  });

  // Fetch games on mount
  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/games`);
        if (!response.ok) throw new Error('Failed to fetch games');
        const data = await response.json();
        setGames(data);
      } catch (error) {
        console.error('Error fetching games:', error);
        setMessage({ type: 'error', text: 'Failed to load games' });
      }
    };

    fetchGames();
  }, []);

  // Fetch config on mount
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/config/all`);
        if (!response.ok) throw new Error('Failed to fetch config');
        const data = await response.json();
        setConfig(data);
      } catch (error) {
        console.error('Error fetching config:', error);
        setMessage({ type: 'error', text: 'Failed to load configuration' });
      }
    };

    fetchConfig();
  }, []);

  // Fetch pieces when game changes
  useEffect(() => {
    if (formData.game_id === null) {
      setPieces([]);
      return;
    }

    const fetchPieces = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/pieces?game_id=${formData.game_id}`);
        if (!response.ok) throw new Error('Failed to fetch pieces');
        const data = await response.json();
        setPieces(data);
      } catch (error) {
        console.error('Error fetching pieces:', error);
        setMessage({ type: 'error', text: 'Failed to load pieces' });
      }
    };

    fetchPieces();
  }, [formData.game_id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.game_id || !formData.piece_id) {
      setMessage({ type: 'error', text: 'Please select both game and piece' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/ml/captureandsetlights`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_id: formData.game_id,
          piece_id: formData.piece_id,
          position_id: formData.position_id,
          rotation: formData.rotation,
          lighting_level: formData.lighting_level,
          lighting_temp: formData.lighting_temp,
          notes: formData.notes || undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Capture failed');
      }

      const result = await response.json();
      
      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: `Image captured successfully! Metadata ID: ${result.image_metadata_id}` 
        });
      } else {
        setMessage({ 
          type: 'error', 
          text: result.message || 'Capture failed' 
        });
      }
    } catch (error) {
      console.error('Error capturing image:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to capture image' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="panel">
      <h1>ML Training Image Capture</h1>

      {message && (
        <div className={`status-message ${message.type === 'success' ? 'ok' : 'error'}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-container">
          <div className="form-row">
            <div className="form-field">
              <label>Game</label>
              <select
                value={formData.game_id || ''}
                onChange={(e) => {
                  const value = e.target.value ? parseInt(e.target.value) : null;
                  setFormData({ ...formData, game_id: value, piece_id: null });
                }}
                required
              >
                <option value="">Select a game</option>
                {games.map((game) => (
                  <option key={game.id} value={game.id}>
                    {game.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Piece</label>
              <select
                value={formData.piece_id || ''}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  piece_id: e.target.value ? parseInt(e.target.value) : null 
                })}
                disabled={!formData.game_id || pieces.length === 0}
                required
              >
                <option value="">Select a piece</option>
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
              <label>Position</label>
              <select
                value={formData.position_id}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  position_id: parseInt(e.target.value) 
                })}
                disabled={!config}
                required
              >
                {config?.object.positionNames.map((name, index) => (
                  <option key={index} value={index}>
                    {name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Rotation</label>
              <select
                value={formData.rotation}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  rotation: parseInt(e.target.value) 
                })}
                disabled={!config}
                required
              >
                {config?.object.rotations.map((rotation) => (
                  <option key={rotation} value={rotation}>
                    {rotation}°
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Light Intensity: {formData.lighting_level}%</label>
              <select
                value={formData.lighting_level}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  lighting_level: parseInt(e.target.value) 
                })}
                disabled={!config}
                required
              >
                {config?.lightSettings.intensity.map((level) => (
                  <option key={level} value={level}>
                    {level}%
                  </option>
                ))}
              </select>
            </div>

            <div className="form-field">
              <label>Light Temperature</label>
              <select
                value={formData.lighting_temp}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  lighting_temp: e.target.value 
                })}
                disabled={!config}
                required
              >
                {config?.lightSettings.tempNames.map((tempName) => (
                  <option key={tempName} value={tempName}>
                    {tempName.charAt(0).toUpperCase() + tempName.slice(1)} ({config.lightSettings.temps[tempName as keyof typeof config.lightSettings.temps]}K)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-field">
            <label>Notes (Optional)</label>
            <textarea
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              rows={3}
              placeholder="Any additional notes about this capture..."
            />
          </div>

          <div className="actions">
            <button
              type="submit"
              disabled={loading || !formData.game_id || !formData.piece_id}
            >
              {loading ? 'Capturing...' : 'Capture Image'}
            </button>
          </div>
        </div>
      </form>

      {loading && (
        <div className="status-message info">
          <p>Setting lights and waiting for stabilization (10s)...</p>
        </div>
      )}
    </div>
  );
}