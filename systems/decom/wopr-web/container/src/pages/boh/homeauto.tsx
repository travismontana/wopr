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

import React, { useState, useEffect } from "react";

import { apiUrl } from "@lib/api";
const API_URL = apiUrl;
interface PresetOptions {
  brightness_options: number[];
  kelvin_options: number[];
  kelvin_descriptions: Record<string, string>;
}

type StatusState =
  | { type: "ok" | "error" | "info"; message: string }
  | null;

export default function HomeAutoPage() {
  const [options, setOptions] = useState<PresetOptions | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<StatusState>(null);

  useEffect(() => {
    loadPresetOptions();
  }, []);

  async function loadPresetOptions() {
    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(
        `${API_URL}/api/v1/homeauto/lights/preset/options`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setOptions(data);
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to load preset options",
      });
    } finally {
      setLoading(false);
    }
  }

  async function handlePresetClick(kelvin: number, brightness: number) {
    setLoading(true);
    setStatus(null);

    try {
      const res = await fetch(`${API_URL}/api/v1/homeauto/lights/preset`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brightness, kelvin }),
      });

      if (!res.ok) {
        const errorText = await res.text();
        throw new Error(`HTTP ${res.status}: ${errorText}`);
      }

      const data = await res.json();
      console.log("Preset activated:", data);

      setStatus({
        type: "ok",
        message: `Activated: ${options?.kelvin_descriptions[kelvin]} @ ${brightness}%`,
      });
    } catch (e: any) {
      setStatus({
        type: "error",
        message: e?.message ?? "Failed to activate preset",
      });
    } finally {
      setLoading(false);
    }
  }

  if (loading && !options) {
    return (
      <section className="panel">
        <h1>Home Automation - Light Presets</h1>
        <p>Loading preset options...</p>
      </section>
    );
  }

  if (!options) {
    return (
      <section className="panel">
        <h1>Home Automation - Light Presets</h1>
        <div className="status-message error">
          Failed to load preset options
        </div>
        <button onClick={loadPresetOptions}>Retry</button>
      </section>
    );
  }

  return (
    <section className="panel">
      <h1>Home Automation - Light Presets</h1>

      {status && (
        <div className={`status-message ${status.type}`}>{status.message}</div>
      )}

      <div className="toolbar">
        <button onClick={loadPresetOptions} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <div className="preset-grid">
        {options.brightness_options.map((brightness) => (
          <div key={brightness} className="preset-row">
            {options.kelvin_options.map((kelvin) => (
              <button
                key={`${kelvin}-${brightness}`}
                className="preset-button"
                onClick={() => handlePresetClick(kelvin, brightness)}
                disabled={loading}
              >
                {options.kelvin_descriptions[kelvin]}/{brightness}%
              </button>
            ))}
          </div>
        ))}
      </div>

      <style>{`
        .preset-grid {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          margin-top: 1rem;
        }

        .preset-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 0.5rem;
        }

        .preset-button {
          padding: 1rem;
          min-height: 3rem;
          font-size: 1rem;
          text-align: center;
        }
      `}</style>
    </section>
  );
}