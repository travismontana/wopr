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

import { Outlet, NavLink } from "react-router-dom";
import "./app.css";

export default function App() {
  return (
    <div className="app">
      <header className="masthead">
        <h1 className="system-name">WOPR</h1>
        <p className="system-tagline">Wargaming Oversight & Position Recognition</p>
      </header>

      <nav className="primary-nav" role="navigation" aria-label="Primary">
        <ul>
          <li><NavLink to="/">Home</NavLink></li>
          <li><NavLink to="/play">Play</NavLink></li>
          <li><NavLink to="/boh">Back of House</NavLink></li>
        </ul>
      </nav>

      <main className="content" role="main">
        <Outlet />
      </main>

      <footer className="system-status" role="contentinfo">
        <span className="status-indicator" data-status="operational">SYS:OK</span>
        <span className="version">v{import.meta.env.VITE_VERSION || '0.0.0'}</span>
      </footer>
    </div>
  );
}
