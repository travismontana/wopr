import { useState, useEffect } from 'react';

interface MLImageMetadata {
  id: number;
  game_id: number;
  piece_id: number;
  position_id: number;
  rotation: number;
  lighting_level: number;
  lighting_temp: string;
  filename: string;
  notes?: string;
  created_at: string;
  game_name?: string;
  piece_name?: string;
}

type SortField = 'id' | 'game_name' | 'piece_name' | 'position_id' | 'rotation' | 'lighting_level' | 'created_at';
type SortDirection = 'asc' | 'desc';

const API_URL =
  (window as any).ENV?.WOPR_API_URL ||
  "https://wopr-api.studio.abode.tailandtraillabs.org";
const API_BASE = API_URL;

export default function MLExplorerPage() {
  const [images, setImages] = useState<MLImageMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1/ml/images`);
      if (!response.ok) throw new Error('Failed to fetch images');
      const data = await response.json();
      setImages(data);
    } catch (error) {
      console.error('Error fetching images:', error);
      setMessage({ type: 'error', text: 'Failed to load image metadata' });
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const sortedImages = [...images].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    
    let comparison = 0;
    if (aVal < bVal) comparison = -1;
    if (aVal > bVal) comparison = 1;
    
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelected(new Set(images.map(img => img.id)));
    } else {
      setSelected(new Set());
    }
  };

  const handleSelectOne = (id: number, checked: boolean) => {
    const newSelected = new Set(selected);
    if (checked) {
      newSelected.add(id);
    } else {
      newSelected.delete(id);
    }
    setSelected(newSelected);
  };

  const handleDelete = async () => {
    if (selected.size === 0) return;

    const confirmed = window.confirm(
      `Delete ${selected.size} image(s)? This cannot be undone.`
    );

    if (!confirmed) return;

    setLoading(true);
    setMessage(null);

    try {
      const deletePromises = Array.from(selected).map(id =>
        fetch(`${API_BASE}/api/v1/ml/images/${id}`, { method: 'DELETE' })
      );

      const results = await Promise.all(deletePromises);
      const failures = results.filter(r => !r.ok);

      if (failures.length > 0) {
        throw new Error(`Failed to delete ${failures.length} image(s)`);
      }

      setMessage({ 
        type: 'success', 
        text: `Successfully deleted ${selected.size} image(s)` 
      });
      setSelected(new Set());
      await fetchImages();
    } catch (error) {
      console.error('Error deleting images:', error);
      setMessage({ 
        type: 'error', 
        text: error instanceof Error ? error.message : 'Failed to delete images' 
      });
    } finally {
      setLoading(false);
    }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <span className="sort-icon">⇅</span>;
    return <span className="sort-icon">{sortDirection === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div className="panel">
      <h1>ML Training Data Explorer</h1>

      {message && (
        <div className={`status-message ${message.type === 'success' ? 'ok' : 'error'}`}>
          {message.text}
        </div>
      )}

      <div className="actions">
        <button
          onClick={handleDelete}
          disabled={selected.size === 0 || loading}
          className="danger"
        >
          Delete Selected ({selected.size})
        </button>
      </div>

      {loading && <div className="status-message info">Loading...</div>}

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  checked={selected.size === images.length && images.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
              </th>
              <th onClick={() => handleSort('id')} style={{ cursor: 'pointer' }}>
                ID <SortIcon field="id" />
              </th>
              <th onClick={() => handleSort('game_name')} style={{ cursor: 'pointer' }}>
                Game <SortIcon field="game_name" />
              </th>
              <th onClick={() => handleSort('piece_name')} style={{ cursor: 'pointer' }}>
                Piece <SortIcon field="piece_name" />
              </th>
              <th onClick={() => handleSort('position_id')} style={{ cursor: 'pointer' }}>
                Position <SortIcon field="position_id" />
              </th>
              <th onClick={() => handleSort('rotation')} style={{ cursor: 'pointer' }}>
                Rotation <SortIcon field="rotation" />
              </th>
              <th onClick={() => handleSort('lighting_level')} style={{ cursor: 'pointer' }}>
                Light % <SortIcon field="lighting_level" />
              </th>
              <th>Temp</th>
              <th>Filename</th>
              <th onClick={() => handleSort('created_at')} style={{ cursor: 'pointer' }}>
                Created <SortIcon field="created_at" />
              </th>
            </tr>
          </thead>
          <tbody>
            {sortedImages.map((img) => (
              <tr key={img.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selected.has(img.id)}
                    onChange={(e) => handleSelectOne(img.id, e.target.checked)}
                  />
                </td>
                <td>{img.id}</td>
                <td>{img.game_name || img.game_id}</td>
                <td>{img.piece_name || img.piece_id}</td>
                <td>{img.position_id}</td>
                <td>{img.rotation}°</td>
                <td>{img.lighting_level}%</td>
                <td>{img.lighting_temp}</td>
                <td className="filename">{img.filename}</td>
                <td>{new Date(img.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {images.length === 0 && !loading && (
        <div className="status-message info">No images captured yet</div>
      )}
    </div>
  );
}