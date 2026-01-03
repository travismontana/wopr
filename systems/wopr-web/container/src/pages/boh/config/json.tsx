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
      const res = await fetch(`${apiUrl}/api/v1/config/all`);
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
      const res = await fetch(`${apiUrl}/api/v1/config/set/${key}`, {
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
      const res = await fetch(`${apiUrl}/api/v1/config/delete/${key}`, {
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
            theme="atom"
            enableClipboard={true}
            dark={true}
            editable={true}
            onEdit={handleEdit}
            onAdd={handleAdd}
            onDelete={handleDelete}
            collapsed={1}
            displayDataTypes={true}
          />
        )}
      </div>
    </div>
  );
}