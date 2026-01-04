import React, { useEffect, useState } from 'react';
import JsonView from 'react18-json-view';
import 'react18-json-view/src/style.css';
import { apiUrl } from '@lib/api';

/*
 * This will grab the json from ${apiUrl}/api/v1/config/all?environment=${env}
 * the page will ask which enviroment to load, which will come from 
 * ${apiUrl}/api/v1/config/environments, which returns something like:
 * [{"environment":"production"},{"environment":"stage"}]
 * Then the user can select which environment to load the config for in a dropdown, 
 * when they select, it will load that config to view using react18-json-view to render it.
 * No styling is required.
 */

const ApiView: React.FC = () => {
  const [environments, setEnvironments] = useState<string[]>([]);
  const [selectedEnv, setSelectedEnv] = useState<string>('');
  const [configData, setConfigData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch available environments
    fetch(`${apiUrl}/api/v1/config/environments`)
      .then((res) => res.json())
      .then((data) => {
        const envs = data.map((item: any) => item.environment);
        setEnvironments(envs);
        if (envs.length > 0) {
          setSelectedEnv(envs[0]);
        }
      })
      .catch((err) => setError(`Error fetching environments: ${err.message}`));
  }, []);

  useEffect(() => {
    if (selectedEnv) {
      setLoading(true);
      fetch(`${apiUrl}/api/v1/config/all?environment=${selectedEnv}`)
        .then((res) => res.json())
        .then((data) => {
          setConfigData(data);
          setLoading(false);
        })
        .catch((err) => {
          setError(`Error fetching config for ${selectedEnv}: ${err.message}`);
          setLoading(false);
        });
    }
  }, [selectedEnv]);

  return (
    <div>
      <h1>API Configuration Viewer</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <label htmlFor="env-select">Select Environment: </label>
      <select
        id="env-select"
        value={selectedEnv}
        onChange={(e) => setSelectedEnv(e.target.value)}
      >
        {environments.map((env) => (
          <option key={env} value={env}>
            {env}
          </option>
        ))}
      </select>
      {loading && <p>Loading configuration...</p>}
      {configData && (
        <div style={{ marginTop: '20px' }}>
          <JsonView 
            src={configData} 
            collapsed={2}
            className="panel"
            theme="atom"
            enableClipboard={true}
            dark={true}
            editable={true} />
        </div>
      )}
    </div>
  );
}
   