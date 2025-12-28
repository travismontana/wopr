import { useState, useEffect } from 'react';

interface ConfigSetting {
  key: string;
  value: any;
  value_type: string;
  description: string;
  environment: string;
}

interface GroupedConfigs {
  [section: string]: ConfigSetting[];
}

export default function ConfigEditor() {
  const [configs, setConfigs] = useState<GroupedConfigs>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [saving, setSaving] = useState(false);
  
  // Track which complex values are expanded
  const [expandedKeys, setExpandedKeys] = useState<Set<string>>(new Set());
  
  // Add new setting state
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [addSection, setAddSection] = useState<string>('');
  const [newKey, setNewKey] = useState<string>('');
  const [newValue, setNewValue] = useState<string>('');
  const [newType, setNewType] = useState<string>('string');
  const [newDescription, setNewDescription] = useState<string>('');

  const API_BASE = '/api/v1/config';

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/all`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Flatten nested config into list of settings with full dot-notation keys
      const flatSettings = flattenConfig(data);
      
      // Group by prefix (e.g., "storage", "camera", "filenames")
      const grouped = groupBySection(flatSettings);
      
      setConfigs(grouped);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load configs');
      console.error('Config fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const flattenConfig = (obj: any, prefix = ''): ConfigSetting[] => {
    const result: ConfigSetting[] = [];
    
    for (const [key, value] of Object.entries(obj)) {
      const fullKey = prefix ? `${prefix}.${key}` : key;
      
      if (value && typeof value === 'object' && !Array.isArray(value)) {
        // Recursively flatten nested objects
        result.push(...flattenConfig(value, fullKey));
      } else {
        // This is a leaf value
        result.push({
          key: fullKey,
          value: value,
          value_type: inferType(value),
          description: '',
          environment: 'default'
        });
      }
    }
    
    return result;
  };

  const inferType = (value: any): string => {
    if (typeof value === 'string') return 'string';
    if (typeof value === 'number') return Number.isInteger(value) ? 'integer' : 'float';
    if (typeof value === 'boolean') return 'boolean';
    if (Array.isArray(value)) return 'list';
    if (typeof value === 'object' && value !== null) return 'dict';
    return 'string';
  };

  const groupBySection = (settings: ConfigSetting[]): GroupedConfigs => {
    const grouped: GroupedConfigs = {};
    
    for (const setting of settings) {
      const section = setting.key.split('.')[0] || 'other';
      if (!grouped[section]) {
        grouped[section] = [];
      }
      grouped[section].push(setting);
    }
    
    // Sort keys within each section
    Object.keys(grouped).forEach(section => {
      grouped[section].sort((a, b) => a.key.localeCompare(b.key));
    });
    
    return grouped;
  };

  const handleEdit = (key: string, currentValue: any) => {
    setEditingKey(key);
    // Convert value to string for editing
    if (typeof currentValue === 'object') {
      setEditValue(JSON.stringify(currentValue));
    } else {
      setEditValue(String(currentValue));
    }
  };

  const handleCancel = () => {
    setEditingKey(null);
    setEditValue('');
  };

  const handleSave = async (key: string, valueType: string) => {
    try {
      setSaving(true);
      
      // Parse value based on type
      let parsedValue: any;
      try {
        if (valueType === 'list' || valueType === 'dict') {
          parsedValue = JSON.parse(editValue);
        } else if (valueType === 'integer') {
          parsedValue = parseInt(editValue, 10);
        } else if (valueType === 'float') {
          parsedValue = parseFloat(editValue);
        } else if (valueType === 'boolean') {
          parsedValue = editValue.toLowerCase() === 'true';
        } else {
          parsedValue = editValue;
        }
      } catch (err) {
        throw new Error('Invalid value format');
      }

      const response = await fetch(`${API_BASE}/set/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: parsedValue,
          updated_by: 'web-ui'
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.statusText}`);
      }

      // Refresh configs after save
      await fetchConfigs();
      setEditingKey(null);
      setEditValue('');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save config');
    } finally {
      setSaving(false);
    }
  };

  const openAddDialog = (section?: string) => {
    setAddSection(section || '');
    setNewKey('');
    setNewValue('');
    setNewType('string');
    setNewDescription('');
    setShowAddDialog(true);
  };

  const closeAddDialog = () => {
    setShowAddDialog(false);
    setAddSection('');
    setNewKey('');
    setNewValue('');
    setNewType('string');
    setNewDescription('');
  };

  const handleAddSetting = async () => {
    try {
      // Build full key
      let fullKey = newKey.trim();
      if (addSection) {
        // Adding to existing section: section.newkey
        fullKey = `${addSection}.${fullKey}`;
      }

      if (!fullKey) {
        throw new Error('Key cannot be empty');
      }

      // Validate key format (alphanumeric, dots, underscores)
      if (!/^[a-zA-Z0-9._]+$/.test(fullKey)) {
        throw new Error('Key can only contain letters, numbers, dots, and underscores');
      }

      // Parse value based on type
      let parsedValue: any;
      try {
        if (newType === 'list' || newType === 'dict') {
          parsedValue = JSON.parse(newValue);
        } else if (newType === 'integer') {
          parsedValue = parseInt(newValue, 10);
          if (isNaN(parsedValue)) throw new Error('Invalid integer');
        } else if (newType === 'float') {
          parsedValue = parseFloat(newValue);
          if (isNaN(parsedValue)) throw new Error('Invalid float');
        } else if (newType === 'boolean') {
          parsedValue = newValue.toLowerCase() === 'true';
        } else {
          parsedValue = newValue;
        }
      } catch (err) {
        throw new Error('Invalid value format for type ' + newType);
      }

      setSaving(true);

      const response = await fetch(`${API_BASE}/set/${fullKey}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: parsedValue,
          description: newDescription || null,
          updated_by: 'web-ui'
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to add: ${response.statusText} - ${errorText}`);
      }

      // Success - refresh and close
      await fetchConfigs();
      closeAddDialog();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to add config');
    } finally {
      setSaving(false);
    }
  };

  const formatValue = (value: any): string => {
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  };

  const toggleExpand = (key: string) => {
    setExpandedKeys(prev => {
      const next = new Set(prev);
      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }
      return next;
    });
  };

  const isComplex = (value: any): boolean => {
    return typeof value === 'object' && value !== null;
  };

  const updateComplexValue = async (key: string, newValue: any, valueType: string) => {
    try {
      setSaving(true);
      
      const response = await fetch(`${API_BASE}/set/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          value: newValue,
          updated_by: 'web-ui'
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to save: ${response.statusText}`);
      }

      await fetchConfigs();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save config');
    } finally {
      setSaving(false);
    }
  };

  const handleArrayItemEdit = async (key: string, value: any[], index: number, newItemValue: string) => {
    const updated = [...value];
    // Try to parse as JSON first, fallback to string
    try {
      updated[index] = JSON.parse(newItemValue);
    } catch {
      updated[index] = newItemValue;
    }
    await updateComplexValue(key, updated, 'list');
  };

  const handleArrayItemDelete = async (key: string, value: any[], index: number) => {
    const updated = value.filter((_, i) => i !== index);
    await updateComplexValue(key, updated, 'list');
  };

  const handleArrayItemAdd = async (key: string, value: any[]) => {
    const updated = [...value, ""];
    await updateComplexValue(key, updated, 'list');
  };

  const handleObjectKeyEdit = async (key: string, value: object, oldKey: string, newKey: string, newValue: string) => {
    const updated = { ...value };
    delete (updated as any)[oldKey];
    // Try to parse as JSON first, fallback to string
    try {
      (updated as any)[newKey] = JSON.parse(newValue);
    } catch {
      (updated as any)[newKey] = newValue;
    }
    await updateComplexValue(key, updated, 'dict');
  };

  const handleObjectKeyDelete = async (key: string, value: object, objKey: string) => {
    const updated = { ...value };
    delete (updated as any)[objKey];
    await updateComplexValue(key, updated, 'dict');
  };

  const handleObjectKeyAdd = async (key: string, value: object) => {
    const updated = { ...value, "": "" };
    await updateComplexValue(key, updated, 'dict');
  };

  if (loading) {
    return <div className="config-editor loading">Loading configurations...</div>;
  }

  if (error) {
    return (
      <div className="config-editor error">
        <h3>Error Loading Configs</h3>
        <p>{error}</p>
        <button onClick={fetchConfigs}>Retry</button>
      </div>
    );
  }

  const sections = Object.keys(configs).sort();

  return (
    <div className="config-editor">
      <div className="config-header">
        <h2>Configuration Editor</h2>
        <div className="header-actions">
          <button onClick={() => openAddDialog()} className="btn-add-section">
            + New Section
          </button>
          <button onClick={fetchConfigs} disabled={loading}>
            ↻ Refresh
          </button>
        </div>
      </div>

      {sections.map(section => (
        <section key={section} className="config-section">
          <div className="section-header">
            <h3>{section}</h3>
            <button 
              onClick={() => openAddDialog(section)}
              className="btn-add-setting"
            >
              + Add Setting
            </button>
          </div>
          <table className="config-table">
            <thead>
              <tr>
                <th>Key</th>
                <th>Value</th>
                <th>Type</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {configs[section].map(setting => (
                <tr key={setting.key}>
                  <td className="key-cell" title={setting.description}>
                    {setting.key}
                  </td>
                  <td className="value-cell">
                    {editingKey === setting.key ? (
                      <input
                        type="text"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        autoFocus
                        className="value-input"
                      />
                    ) : isComplex(setting.value) ? (
                      <div className="complex-value">
                        <button 
                          onClick={() => toggleExpand(setting.key)}
                          className="btn-expand"
                        >
                          {expandedKeys.has(setting.key) ? '▼' : '▶'} 
                          {Array.isArray(setting.value) ? `[${setting.value.length} items]` : `{${Object.keys(setting.value).length} keys}`}
                        </button>
                        
                        {expandedKeys.has(setting.key) && (
                          <div className="nested-editor">
                            {Array.isArray(setting.value) ? (
                              <div className="array-editor">
                                {setting.value.map((item, idx) => (
                                  <div key={idx} className="array-item">
                                    <span className="item-index">[{idx}]</span>
                                    <input
                                      type="text"
                                      value={typeof item === 'object' ? JSON.stringify(item) : String(item)}
                                      onChange={(e) => {
                                        const newVal = [...setting.value];
                                        try {
                                          newVal[idx] = JSON.parse(e.target.value);
                                        } catch {
                                          newVal[idx] = e.target.value;
                                        }
                                        // Update in real-time without save button
                                      }}
                                      onBlur={(e) => handleArrayItemEdit(setting.key, setting.value, idx, e.target.value)}
                                      className="nested-input"
                                    />
                                    <button
                                      onClick={() => handleArrayItemDelete(setting.key, setting.value, idx)}
                                      className="btn-delete-nested"
                                      disabled={saving}
                                    >
                                      ✗
                                    </button>
                                  </div>
                                ))}
                                <button
                                  onClick={() => handleArrayItemAdd(setting.key, setting.value)}
                                  className="btn-add-nested"
                                  disabled={saving}
                                >
                                  + Add Item
                                </button>
                              </div>
                            ) : (
                              <div className="object-editor">
                                {Object.entries(setting.value).map(([objKey, objVal]) => (
                                  <div key={objKey} className="object-item">
                                    <input
                                      type="text"
                                      value={objKey}
                                      onChange={(e) => {
                                        // Key edit - will be handled on blur
                                      }}
                                      onBlur={(e) => {
                                        if (e.target.value !== objKey) {
                                          const valStr = typeof objVal === 'object' ? JSON.stringify(objVal) : String(objVal);
                                          handleObjectKeyEdit(setting.key, setting.value, objKey, e.target.value, valStr);
                                        }
                                      }}
                                      className="nested-input key-input"
                                      placeholder="key"
                                    />
                                    <span className="key-separator">:</span>
                                    <input
                                      type="text"
                                      value={typeof objVal === 'object' ? JSON.stringify(objVal) : String(objVal)}
                                      onChange={(e) => {
                                        // Value edit - will be handled on blur
                                      }}
                                      onBlur={(e) => handleObjectKeyEdit(setting.key, setting.value, objKey, objKey, e.target.value)}
                                      className="nested-input value-input"
                                      placeholder="value"
                                    />
                                    <button
                                      onClick={() => handleObjectKeyDelete(setting.key, setting.value, objKey)}
                                      className="btn-delete-nested"
                                      disabled={saving}
                                    >
                                      ✗
                                    </button>
                                  </div>
                                ))}
                                <button
                                  onClick={() => handleObjectKeyAdd(setting.key, setting.value)}
                                  className="btn-add-nested"
                                  disabled={saving}
                                >
                                  + Add Property
                                </button>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    ) : (
                      <code>{formatValue(setting.value)}</code>
                    )}
                  </td>
                  <td className="type-cell">
                    <span className={`type-badge type-${setting.value_type}`}>
                      {setting.value_type}
                    </span>
                  </td>
                  <td className="actions-cell">
                    {editingKey === setting.key ? (
                      <>
                        <button 
                          onClick={() => handleSave(setting.key, setting.value_type)}
                          disabled={saving}
                          className="btn-save"
                        >
                          ✓
                        </button>
                        <button 
                          onClick={handleCancel}
                          disabled={saving}
                          className="btn-cancel"
                        >
                          ✗
                        </button>
                      </>
                    ) : isComplex(setting.value) ? (
                      <button 
                        onClick={() => toggleExpand(setting.key)}
                        className="btn-edit"
                      >
                        {expandedKeys.has(setting.key) ? 'Collapse' : 'Expand'}
                      </button>
                    ) : (
                      <button 
                        onClick={() => handleEdit(setting.key, setting.value)}
                        className="btn-edit"
                      >
                        Edit
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}

      {showAddDialog && (
        <div className="modal-overlay" onClick={closeAddDialog}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>
              {addSection ? `Add Setting to ${addSection}` : 'Add New Section'}
            </h3>
            
            <div className="form-group">
              <label>
                {addSection ? 'Setting Name (suffix)' : 'Key (use dots for sections)'}
              </label>
              <input
                type="text"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                placeholder={addSection ? 'new_setting' : 'newsection.setting'}
                className="form-input"
              />
              {addSection && (
                <small>Full key: {addSection}.{newKey}</small>
              )}
            </div>

            <div className="form-group">
              <label>Type</label>
              <select 
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
                className="form-input"
              >
                <option value="string">string</option>
                <option value="integer">integer</option>
                <option value="float">float</option>
                <option value="boolean">boolean</option>
                <option value="list">list (JSON array)</option>
                <option value="dict">dict (JSON object)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Value</label>
              {newType === 'boolean' ? (
                <select 
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  className="form-input"
                >
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              ) : (
                <input
                  type="text"
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  placeholder={
                    newType === 'list' ? '["item1", "item2"]' :
                    newType === 'dict' ? '{"key": "value"}' :
                    newType === 'integer' ? '42' :
                    newType === 'float' ? '3.14' :
                    'value'
                  }
                  className="form-input"
                />
              )}
            </div>

            <div className="form-group">
              <label>Description (optional)</label>
              <input
                type="text"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                placeholder="Description of this setting"
                className="form-input"
              />
            </div>

            <div className="modal-actions">
              <button 
                onClick={handleAddSetting}
                disabled={saving || !newKey.trim() || !newValue.trim()}
                className="btn-save"
              >
                {saving ? 'Adding...' : 'Add Setting'}
              </button>
              <button 
                onClick={closeAddDialog}
                disabled={saving}
                className="btn-cancel"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .config-editor {
          padding: 1rem;
          max-width: 1400px;
          margin: 0 auto;
        }

        .config-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 2px solid #333;
        }

        .config-header h2 {
          margin: 0;
          color: #0f0;
          font-family: monospace;
        }

        .header-actions {
          display: flex;
          gap: 0.5rem;
        }

        .config-header button {
          background: #080;
          color: #0f0;
          border: 1px solid #0f0;
          padding: 0.5rem 1rem;
          cursor: pointer;
          font-family: monospace;
        }

        .btn-add-section {
          background: #004 !important;
          color: #0ff !important;
          border-color: #0ff !important;
        }

        .btn-add-section:hover:not(:disabled) {
          background: #006 !important;
        }

        .config-header button:hover:not(:disabled) {
          background: #0a0;
        }

        .config-header button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .config-section {
          margin-bottom: 2rem;
        }

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .config-section h3 {
          color: #0f0;
          font-family: monospace;
          margin: 0;
          text-transform: uppercase;
          font-size: 1.1rem;
        }

        .btn-add-setting {
          background: #004;
          color: #0ff;
          border: 1px solid #0ff;
          padding: 0.25rem 0.75rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 0.9rem;
        }

        .btn-add-setting:hover {
          background: #006;
        }

        .config-table {
          width: 100%;
          border-collapse: collapse;
          background: #000;
          border: 1px solid #333;
        }

        .config-table th {
          background: #111;
          color: #0f0;
          text-align: left;
          padding: 0.75rem;
          border: 1px solid #333;
          font-family: monospace;
          font-weight: normal;
          text-transform: uppercase;
          font-size: 0.9rem;
        }

        .config-table td {
          padding: 0.5rem 0.75rem;
          border: 1px solid #222;
          color: #0f0;
          font-family: monospace;
        }

        .config-table tr:hover {
          background: #111;
        }

        .key-cell {
          font-weight: bold;
          max-width: 300px;
        }

        .value-cell {
          max-width: 500px;
          overflow-x: auto;
        }

        .value-cell code {
          color: #0ff;
          font-family: monospace;
        }

        .value-input {
          width: 100%;
          background: #111;
          color: #0ff;
          border: 1px solid #0f0;
          padding: 0.25rem 0.5rem;
          font-family: monospace;
        }

        .value-input:focus {
          outline: none;
          border-color: #0ff;
          box-shadow: 0 0 5px #0ff;
        }

        .type-cell {
          width: 100px;
        }

        .type-badge {
          display: inline-block;
          padding: 0.2rem 0.5rem;
          border-radius: 3px;
          font-size: 0.8rem;
          text-transform: uppercase;
        }

        .type-string { background: #222; color: #0f0; }
        .type-integer { background: #220; color: #ff0; }
        .type-float { background: #220; color: #ff0; }
        .type-boolean { background: #202; color: #f0f; }
        .type-list { background: #022; color: #0ff; }
        .type-dict { background: #022; color: #0ff; }

        .actions-cell {
          width: 120px;
          text-align: center;
        }

        .btn-edit, .btn-save, .btn-cancel {
          background: #080;
          color: #0f0;
          border: 1px solid #0f0;
          padding: 0.25rem 0.75rem;
          margin: 0 0.25rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 0.9rem;
        }

        .btn-edit:hover:not(:disabled) {
          background: #0a0;
        }

        .btn-save {
          background: #004;
          color: #0ff;
          border-color: #0ff;
        }

        .btn-save:hover:not(:disabled) {
          background: #006;
        }

        .btn-cancel {
          background: #400;
          color: #f00;
          border-color: #f00;
        }

        .btn-cancel:hover:not(:disabled) {
          background: #600;
        }

        button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading, .error {
          padding: 2rem;
          text-align: center;
          color: #0f0;
          font-family: monospace;
        }

        .error {
          color: #f00;
        }

        .error button {
          margin-top: 1rem;
        }

        /* Modal styles */
        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.8);
          display: flex;
          justify-content: center;
          align-items: center;
          z-index: 1000;
        }

        .modal-content {
          background: #000;
          border: 2px solid #0f0;
          padding: 2rem;
          max-width: 600px;
          width: 90%;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }

        .modal-content h3 {
          color: #0f0;
          font-family: monospace;
          margin-top: 0;
          margin-bottom: 1.5rem;
          text-transform: uppercase;
        }

        .form-group {
          margin-bottom: 1.5rem;
        }

        .form-group label {
          display: block;
          color: #0f0;
          font-family: monospace;
          margin-bottom: 0.5rem;
          font-size: 0.9rem;
        }

        .form-group small {
          display: block;
          color: #0ff;
          font-family: monospace;
          font-size: 0.8rem;
          margin-top: 0.25rem;
        }

        .form-input {
          width: 100%;
          background: #111;
          color: #0ff;
          border: 1px solid #0f0;
          padding: 0.5rem;
          font-family: monospace;
          font-size: 1rem;
        }

        .form-input:focus {
          outline: none;
          border-color: #0ff;
          box-shadow: 0 0 5px #0ff;
        }

        .modal-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
          margin-top: 2rem;
          padding-top: 1rem;
          border-top: 1px solid #333;
        }

        .modal-actions button {
          padding: 0.5rem 1.5rem;
        }

        /* Complex value editor styles */
        .complex-value {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .btn-expand {
          background: #111;
          color: #0ff;
          border: 1px solid #0ff;
          padding: 0.25rem 0.5rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 0.9rem;
          text-align: left;
          width: fit-content;
        }

        .btn-expand:hover {
          background: #004;
        }

        .nested-editor {
          margin-top: 0.5rem;
          margin-left: 1rem;
          padding: 0.5rem;
          border-left: 2px solid #0ff;
          background: #0a0a0a;
        }

        .array-editor,
        .object-editor {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .array-item,
        .object-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .item-index {
          color: #0f0;
          font-family: monospace;
          font-weight: bold;
          min-width: 2rem;
        }

        .key-separator {
          color: #0ff;
          font-family: monospace;
          font-weight: bold;
        }

        .nested-input {
          flex: 1;
          background: #000;
          color: #0ff;
          border: 1px solid #333;
          padding: 0.25rem 0.5rem;
          font-family: monospace;
          font-size: 0.9rem;
        }

        .nested-input:focus {
          outline: none;
          border-color: #0ff;
          box-shadow: 0 0 3px #0ff;
        }

        .key-input {
          flex: 0 0 30%;
          color: #f0f;
        }

        .btn-delete-nested {
          background: #400;
          color: #f00;
          border: 1px solid #f00;
          padding: 0.25rem 0.5rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 0.9rem;
          min-width: 2rem;
        }

        .btn-delete-nested:hover:not(:disabled) {
          background: #600;
        }

        .btn-add-nested {
          background: #004;
          color: #0ff;
          border: 1px solid #0ff;
          padding: 0.25rem 0.75rem;
          cursor: pointer;
          font-family: monospace;
          font-size: 0.9rem;
          margin-top: 0.25rem;
          align-self: flex-start;
        }

        .btn-add-nested:hover:not(:disabled) {
          background: #006;
        }
      `}</style>
    </div>
  );
}
