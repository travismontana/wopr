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
 * 
 * I'd like to select the theme of react18-json-view with a select box as well, with options:
 * - default | a11y | github | vscode | atom|winter-is-coming
 * And enable/disable  dark mode with a checkbox.
 * 
 * the page auto updates when any of the options change.
 */

export default function WoprConfig() {
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

  const handleThemeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setTheme(e.target.value);
  };

  const handleDarkModeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDarkMode(e.target.checked);
  };

  const [theme, setTheme] = useState<string>('default');
  const [darkMode, setDarkMode] = useState<boolean>(false);



  return (
    <div>
      <h1>WOPR Configuration</h1>
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
      <br /><br />
      <label htmlFor="theme-select">Select Theme: </label>
      <select
        id="theme-select"
        value={theme}
        onChange={handleThemeChange}
      >
        <option value="default">Default</option>
        <option value="a11y">A11y</option>
        <option value="github">GitHub</option>
        <option value="vscode">VSCode</option>
        <option value="atom">Atom</option>
        <option value="winter-is-coming">Winter is Coming</option>
      </select>
      <br /><br />
      <label htmlFor="dark-mode-checkbox">
        <input
          type="checkbox"
          id="dark-mode-checkbox"
          checked={darkMode}
          onChange={handleDarkModeChange}
        />
        Enable Dark Mode
      </label>
      <br /><br />
      {loading && <p>Loading configuration...</p>}
      {configData && (
        <div style={{ marginTop: '20px' }}>
          <JsonView 
            src={configData} 
            collapsed={2}
            className="panel"
            theme={theme}
            enableClipboard={true}
            dark={darkMode}
            editable={false} />
        </div>
      )}
    </div>
  );
}
   