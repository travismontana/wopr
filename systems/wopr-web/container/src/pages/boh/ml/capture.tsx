/*
 * New capture page.
 * Copyright (c) Tailand Trail Labs and its affiliates. All rights reserved.
 *
 * Need config from useConfig()
 * Need game list from ${apiUrl}/api/v2/games
 * Need piece list for that game ${apiUrl}/api/v2/pieces/gameId/
 * 
 * Get the list of games, it returns something like this:
 * {"data":[{"id":4,"status":"published","user_created":"08f72b0e-58c8-4dde-a112-d1256673b441","date_created":"2026-01-04T23:21:59.246Z","user_updated":"08f72b0e-58c8-4dde-a112-d1256673b441","date_updated":"2026-01-04T23:22:14.121Z","uuid":"32c0b170-3e67-441d-bffe-eadcd93c5b3b","name":" Dune: Imperium – Uprising","min_players":1,"max_players":6,"url":"https://boardgamegeek.com/boardgame/397598/dune-imperium-uprising","description":"  In Dune: Imperium Uprising, you want to continue to balance military might with political intrigue, wielding new tools in pursuit of victory. Spies will shore up your plans, vital contracts will expand your resources, or you can learn the ways of the Fremen and ride mighty sandworms into battle!  Dune: Imperium Uprising is a standalone spinoff to Dune: Imperium that expands on that game's blend of deck-building and worker placement, while introducing a new six-player mode that pits two teams against one other in the biggest struggle yet.  The Dune: Imperium expansions Rise of Ix and Immortality work with Uprising, as do almost all of the cards from the base game, and elements of Uprising can be used with Dune: Imperium.  The choices are yours. The Imperium awaits!"}]}
 * So the select will need the name of each.
 * 
 * Once we get the names, we then get the pieces, it looks like:
 * {"data":[{"id":2,"status":"published","user_created":"08f72b0e-58c8-4dde-a112-d1256673b441","date_created":"2026-01-04T23:27:00.663Z","user_updated":"08f72b0e-58c8-4dde-a112-d1256673b441","date_updated":"2026-01-04T23:31:00.426Z","uuid":"ae387f86-6e0c-42ae-967c-129cba905b4e","name":"test","game_catalog_uuid":4},{"id":3,"status":"published","user_created":"08f72b0e-58c8-4dde-a112-d1256673b441","date_created":"2026-01-04T23:30:37.444Z","user_updated":"08f72b0e-58c8-4dde-a112-d1256673b441","date_updated":"2026-01-04T23:31:00.426Z","uuid":"2d2cbdcf-34db-4c3c-8a6e-f3d27370cc6f","name":"1 Solari token","game_catalog_uuid":4},{"id":4,"status":"published","user_created":"08f72b0e-58c8-4dde-a112-d1256673b441","date_created":"2026-01-04T23:30:37.448Z","user_updated":"08f72b0e-58c8-4dde-a112-d1256673b441","date_updated":"2026-01-04T23:31:00.426Z","uuid":"f673de07-af8d-46c8-b8e5-80b623080e04","name":"5 Solari token","game_catalog_uuid":4},
 * So the select will need the name of each piece.
 * 
 * Once we have that, then in the config, we have:
 * "lightSettings": {
    "temp": {
      "warm": 3000,
      "neutral": 4000,
      "cool": 5000
    },
    "intensity": [
      10,
      20,
      30,
      40,
      50,
      60,
      70,
      80,
      90,
      100
    ]
  },
  "object": {
    "rotations": [
      0,
      45,
      90,
      135,
      180,
      225,
      270,
      315
    ],
    "positions": {
      "Center": "center",
      "Near Center": "nearCenter",
      "Random": "random",
      "Top Edge": "topEdge",
      "Bottom Edge": "bottomEdge",
      "Left Edge": "leftEdge",
      "Right Edge": "rightEdge",
      "Top Right": "topRight",
      "Top Left": "topLeft",
      "Bottom Right": "bottomRight",
      "Bottom Left": "bottomLeft"
    }
  },
  "filenames": {
    "mlcapture": {
      "fullImageFilename": "{{piece_id}}-{{game_id}}-{{capture_id}}.jpg",
      "thumbnailFilename": "{{piece_id}}-{{game_id}}-{{capture_id}}-thumb.jpg"
    }
  },
  * 
  * api to create the entry:
  * POST ${apiUrl}/api/v2/mlimages
  * body:
  *   object_rotation_id: <index number of rotation from config>,
  *   object_position_id: <key of position from config>,
  *   lighting_intensity: <intensity number from config>,
  *   lighting_temp: <key of temp from config>,
  *   piece_id: <id from piece select>,
  *   game_id: <id from game select>,
  * 
  *
  * So, we'll create the row in the database, then select the uuid,
  * then generate the filenames, 
  * then call the homeautomation api to set the lights
  * then call the camera to take the pic and store the image
  * 
  */
/*
 * New capture page.
 * Copyright (c) Tailand Trail Labs and its affiliates. All rights reserved.
 */

import { useState, useEffect } from "react";
import { useConfig } from "@/config/ConfigContext";
import { apiUrl } from "@lib/api";

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
  const lightTemp = config.lightSettings.temp;
  const lightIntensity = config.lightSettings.intensity;
  const objectRotations = config.object.rotations;
  const objectPositions = config.object.positions;

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