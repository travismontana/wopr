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

import { useState, useEffect } from 'react';
import { apiUrl } from "@lib/api";

interface MLImageMetadata {
  id: number;
  uuid: string;
  game_uuid: number;
  piece_id: number;
  object_position: string;
  object_rotation: number;
  light_intensity: number;
  color_temp: string;
  filename: string;
  status: string;
  date_created: string;
  date_updated: string | null;
  user_created: string | null;
  user_updated: string | null;
}

type SortField = 'id' | 'game_uuid' | 'piece_id' | 'object_position' | 'object_rotation' | 'light_intensity' | 'date_created';
type SortDirection = 'asc' | 'desc';

const API_BASE = apiUrl;

export function MLExplorerPage() {
  const [images, setImages] = useState<MLImageMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [sortField, setSortField] = useState<SortField>('date_created');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    fetchImages();
  }, []);

  const fetchImages = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/v1/mlimages`);
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
    let aVal: any = a[sortField];
    let bVal: any = b[sortField];
    
    // Handle string positions as numbers for sorting
    if (sortField === 'object_position') {
      aVal = parseInt(aVal) || 0;
      bVal = parseInt(bVal) || 0;
    }
    
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
        fetch(`${API_BASE}/api/v1/mlimages/${id}`, { method: 'DELETE' })
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
              <th onClick={() => handleSort('game_uuid')} style={{ cursor: 'pointer' }}>
                Game <SortIcon field="game_uuid" />
              </th>
              <th onClick={() => handleSort('piece_id')} style={{ cursor: 'pointer' }}>
                Piece <SortIcon field="piece_id" />
              </th>
              <th onClick={() => handleSort('object_position')} style={{ cursor: 'pointer' }}>
                Position <SortIcon field="object_position" />
              </th>
              <th onClick={() => handleSort('object_rotation')} style={{ cursor: 'pointer' }}>
                Rotation <SortIcon field="object_rotation" />
              </th>
              <th onClick={() => handleSort('light_intensity')} style={{ cursor: 'pointer' }}>
                Light % <SortIcon field="light_intensity" />
              </th>
              <th>Temp</th>
              <th>Filename</th>
              <th onClick={() => handleSort('date_created')} style={{ cursor: 'pointer' }}>
                Created <SortIcon field="date_created" />
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
                <td>{img.game_uuid}</td>
                <td>{img.piece_id}</td>
                <td>{img.object_position}</td>
                <td>{img.object_rotation}°</td>
                <td>{img.light_intensity}%</td>
                <td>{img.color_temp}</td>
                <td className="filename">{img.filename}</td>
                <td>{new Date(img.date_created).toLocaleString()}</td>
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