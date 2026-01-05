/*
 * New capture page.
 * Copyright (c) Tailand Trail Labs and its affiliates. All rights reserved.
 */

import { useState, useEffect } from "react";
import { useConfig } from "@/config/ConfigContext";

const apiUrl = "https://api.wopr.tailandtraillabs.org";
interface Game {
  id: number;
  uuid: string;
  name: string;
  status: string;
}

interface Piece {
  id: number;
  uuid: string;
  name: string;
  game_catalog_uuid: number;
}

interface FormData {
  game_id: number | null;
  piece_id: number | null;
  object_rotation_id: number | null;
  object_position_id: string | null;
  lighting_temp: string | null;
  lighting_intensity: number | null;
}

async function getGames() {
  const response = await fetch(`${apiUrl}/api/v2/games`);
  const data = await response.json();
  return data.data as Game[];
}

async function getPieces(gameId: number) {
  const response = await fetch(`${apiUrl}/api/v2/pieces/${gameId}/`);
  const data = await response.json();
  return data.data as Piece[];
}

async function createCapture(formData: FormData) {
  const response = await fetch(`${apiUrl}/api/v2/mlimages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });
  const data = await response.json();
  return data;
}

export default function MLCapturePage() {
  const config = useConfig();

  const [games, setGames] = useState<Game[]>([]);
  const [pieces, setPieces] = useState<Piece[]>([]);
  const [formData, setFormData] = useState<FormData>({
    game_id: null,
    piece_id: null,
    object_rotation_id: null,
    object_position_id: null,
    lighting_temp: null,
    lighting_intensity: null,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  // Load games on mount
  useEffect(() => {
    const loadGames = async () => {
      try {
        const gamesList = await getGames();
        setGames(gamesList);
      } catch (error) {
        console.error('Error loading games:', error);
        setMessage('Error loading games');
      }
    };
    loadGames();
  }, []);
  
  if (!config || !config.lightSettings || !config.object || !config.filenames) {
    return <div>Loading configuration...</div>;
  }

  const lightTemp = config.lightSettings.temp;
  const lightIntensity = config.lightSettings.intensity;
  const objectRotations = config.object.rotations;
  const objectPositions = config.object.positions;

  // Load pieces when game changes
  const handleGameChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const gameId = parseInt(e.target.value);
    setFormData({ ...formData, game_id: gameId, piece_id: null });
    setPieces([]);
    
    if (gameId) {
      try {
        const piecesList = await getPieces(gameId);
        setPieces(piecesList);
      } catch (error) {
        console.error('Error loading pieces:', error);
        setMessage('Error loading pieces');
      }
    }
  };

  const handlePieceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, piece_id: parseInt(e.target.value) });
  };

  const handleRotationChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, object_rotation_id: parseInt(e.target.value) });
  };

  const handlePositionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, object_position_id: e.target.value });
  };

  const handleLightTempChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, lighting_temp: e.target.value });
  };

  const handleLightIntensityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setFormData({ ...formData, lighting_intensity: parseInt(e.target.value) });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate all fields are filled
    if (!formData.game_id || !formData.piece_id || 
        formData.object_rotation_id === null || !formData.object_position_id ||
        !formData.lighting_temp || !formData.lighting_intensity) {
      setMessage('All fields are required');
      return;
    }

    setIsSubmitting(true);
    setMessage(null);

    try {
      const result = await createCapture(formData);
      console.log('Capture created:', result);
      setMessage('Capture initiated successfully');
      
      // Reset form
      setFormData({
        game_id: formData.game_id, // Keep game selected
        piece_id: null,
        object_rotation_id: null,
        object_position_id: null,
        lighting_temp: null,
        lighting_intensity: null,
      });
    } catch (error) {
      console.error('Error creating capture:', error);
      setMessage('Error creating capture');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="ml-capture-page">
      <h1>ML Capture Page</h1>
      <p>Configure and capture images for machine learning training.</p>
      
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="game">Game:</label>
          <select 
            id="game" 
            name="game" 
            value={formData.game_id || ''} 
            onChange={handleGameChange} 
            required
            disabled={isSubmitting}
          >
            <option value="" disabled>Select a game</option>
            {games.map((game) => (
              <option key={game.id} value={game.id}>{game.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="piece">Piece:</label>
          <select 
            id="piece" 
            name="piece" 
            value={formData.piece_id || ''} 
            onChange={handlePieceChange} 
            required
            disabled={!formData.game_id || isSubmitting}
          >
            <option value="" disabled>Select a piece</option>
            {pieces.map((piece) => (
              <option key={piece.id} value={piece.id}>{piece.name}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="rotation">Object Rotation:</label>
          <select 
            id="rotation" 
            name="rotation" 
            value={formData.object_rotation_id !== null ? formData.object_rotation_id : ''} 
            onChange={handleRotationChange} 
            required
            disabled={isSubmitting}
          >
            <option value="" disabled>Select rotation</option>
            {objectRotations.map((degrees, index) => (
              <option key={index} value={index}>{degrees}°</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="position">Object Position:</label>
          <select 
            id="position" 
            name="position" 
            value={formData.object_position_id || ''} 
            onChange={handlePositionChange} 
            required
            disabled={isSubmitting}
          >
            <option value="" disabled>Select position</option>
            {Object.entries(objectPositions).map(([label, value]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="lightTemp">Light Temperature:</label>
          <select 
            id="lightTemp" 
            name="lightTemp" 
            value={formData.lighting_temp || ''} 
            onChange={handleLightTempChange} 
            required
            disabled={isSubmitting}
          >
            <option value="" disabled>Select temperature</option>
            {Object.entries(lightTemp).map(([name, kelvin]) => (
              <option key={name} value={name}>{name} ({kelvin}K)</option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="lightIntensity">Light Intensity:</label>
          <select 
            id="lightIntensity" 
            name="lightIntensity" 
            value={formData.lighting_intensity || ''} 
            onChange={handleLightIntensityChange} 
            required
            disabled={isSubmitting}
          >
            <option value="" disabled>Select intensity</option>
            {lightIntensity.map((value) => (
              <option key={value} value={value}>{value}%</option>
            ))}
          </select>
        </div>

        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Capturing...' : 'Capture Image'}
        </button>
      </form>
    </div>
  );
}