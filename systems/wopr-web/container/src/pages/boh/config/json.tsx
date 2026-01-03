import React, { useEffect, useState } from 'react';
import JsonView from 'react18-json-view';
import 'react18-json-view/src/style.css';
import { apiUrl } from '@lib/api';

interface ConfigData {
  [key: string]: any;
}

export default function JsonConfigPage() {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);
  const [lastSaved, setLastSaved] = useState<string | null>(null);

  // Fetch config on mount
  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${apiUrl}/config/all`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${await res.text()}`);
      }
      const data = await res.json();
      setConfig(data);
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setLoading(false);
    }
  };

  // Convert path array to dot notation key
  const pathToKey = (path: (string | number)[]): string => {
    return path.join('.');
  };

  // Save edited value to API
  const saveValue = async (key: string, value: any) => {
    setSaving(true);
    try {
      const res = await fetch(`${apiUrl}/config/set/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: value,
          updated_by: 'web-ui-json'
        })
      });

      if (!res.ok) {
        throw new Error(`Failed to save ${key}: ${await res.text()}`);
      }

      setLastSaved(`${key} @ ${new Date().toLocaleTimeString()}`);
      
      // Refresh config to get updated values
      await fetchConfig();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setSaving(false);
    }
  };

  // Handle edits from react-json-view
  const handleEdit = async (params: any) => {
    const { newValue, oldValue, namespace } = params;
    
    // namespace is array like ['storage', 'base_path']
    const key = pathToKey(namespace);
    
    await saveValue(key, newValue);
  };

  // Handle additions
  const handleAdd = async (params: any) => {
    const { newValue, namespace } = params;
    const key = pathToKey(namespace);
    
    await saveValue(key, newValue);
  };

  // Handle deletions
  const handleDelete = async (params: any) => {
    const { namespace } = params;
    const key = pathToKey(namespace);
    
    setSaving(true);
    try {
      const res = await fetch(`${apiUrl}/config/delete/${key}`, {
        method: 'DELETE'
      });

      if (!res.ok) {
        throw new Error(`Failed to delete ${key}: ${await res.text()}`);
      }

      setLastSaved(`Deleted ${key} @ ${new Date().toLocaleTimeString()}`);
      await fetchConfig();
    } catch (e: any) {
      setError(e?.message ?? String(e));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="json-config-page">
        <div className="loading">LOADING CONFIGURATION...</div>
      </div>
    );
  }

  if (error && !config) {
    return (
      <div className="json-config-page">
        <div className="error-panel">
          <h3>ERROR</h3>
          <p>{error}</p>
          <button onClick={fetchConfig} className="btn-retry">
            RETRY
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="json-config-page">
      <div className="json-header">
        <div className="header-info">
          <h2>JSON Configuration Editor</h2>
          {lastSaved && <span className="last-saved">Last: {lastSaved}</span>}
        </div>
        <div className="header-actions">
          <button 
            onClick={fetchConfig} 
            disabled={loading || saving}
            className="btn-refresh"
          >
            {loading ? 'LOADING...' : '↻ REFRESH'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ERROR: {error}
          <button onClick={() => setError(null)} className="btn-dismiss">✗</button>
        </div>
      )}

      {saving && (
        <div className="saving-banner">
          SAVING...
        </div>
      )}

      <div className="json-viewer">
        {config && (
          <JsonView 
            src={config}
            theme="winter-is-coming"
            enableClipboard={true}
            editable={true}
            onEdit={handleEdit}
            onAdd={handleAdd}
            onDelete={handleDelete}
            collapsed={1}
            displayDataTypes={false}
          />
        )}
      </div>

      <style>{`
        .json-config-page {
          padding: 1rem;
          max-width: 1600px;
          margin: 0 auto;
          background: #000;
          min-height: 100vh;
        }

        .json-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          border-bottom: 2px solid #0f0;
          margin-bottom: 1rem;
        }

        .header-info h2 {
          margin: 0;
          color: #0f0;
          font-family: monospace;
          font-size: 1.5rem;
        }

        .last-saved {
          display: block;
          color: #0ff;
          font-family: monospace;
          font-size: 0.8rem;
          margin-top: 0.5rem;
        }

        .header-actions {
          display: flex;
          gap: 0.5rem;
        }

        .btn-refresh,
        .btn-retry {
          background: #080;
          color: #0f0;
          border: 1px solid #0f0;
          padding: 0.5rem 1rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 1rem;
        }

        .btn-refresh:hover:not(:disabled),
        .btn-retry:hover {
          background: #0a0;
        }

        .btn-refresh:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading {
          text-align: center;
          padding: 3rem;
          color: #0f0;
          font-family: monospace;
          font-size: 1.2rem;
        }

        .error-panel {
          text-align: center;
          padding: 2rem;
          border: 2px solid #f00;
          background: #200;
        }

        .error-panel h3 {
          color: #f00;
          font-family: monospace;
          margin-top: 0;
        }

        .error-panel p {
          color: #faa;
          font-family: monospace;
        }

        .error-banner {
          background: #400;
          border: 1px solid #f00;
          color: #faa;
          padding: 0.75rem 1rem;
          margin-bottom: 1rem;
          font-family: monospace;
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        .saving-banner {
          background: #004;
          border: 1px solid #0ff;
          color: #0ff;
          padding: 0.75rem 1rem;
          margin-bottom: 1rem;
          font-family: monospace;
          text-align: center;
        }

        .btn-dismiss {
          background: transparent;
          border: none;
          color: #f00;
          cursor: pointer;
          font-size: 1.2rem;
          padding: 0 0.5rem;
        }

        .btn-dismiss:hover {
          color: #fff;
        }

        .json-viewer {
          background: #000;
          padding: 1rem;
          border: 1px solid #333;
          border-radius: 4px;
          overflow-x: auto;
        }

        /* Override react-json-view theme to match WOPR aesthetic */
        .json-viewer .react-json-view {
          background: #000 !important;
          font-family: 'Courier New', Courier, monospace !important;
        }

        .json-viewer .object-key-val {
          color: #0f0 !important;
        }

        .json-viewer .string-value {
          color: #0ff !important;
        }

        .json-viewer .number-value {
          color: #ff0 !important;
        }

        .json-viewer .boolean-value {
          color: #f0f !important;
        }

        .json-viewer .object-key {
          color: #0f0 !important;
        }

        .json-viewer .collapsed-icon,
        .json-viewer .expanded-icon {
          color: #0f0 !important;
        }
      `}</style>
    </div>
  );
}