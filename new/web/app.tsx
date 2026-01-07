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

import { Routes, Route, Link } from "react-router-dom";
import "./pages/css/theme.css";

import Dashboard from "./pages/dashboard";
import GameImages from "./pages/game_images";
import GamesManager from "./pages/GamesManager";
import { ImageGallery } from "./pages/images";
import ML from "./pages/ml";
import Control from "./pages/control";
import PiecesManager from "./pages/PiecesManager";
import MLImagesManager from "./pages/MLImagesManager";

export default function Main() {
  return (
    <div className="app">
      <div className="layout">
        <header className="wopr-header">
          <h1>WOPR</h1>
          <h2>Wargaming Oversight &amp; Position Recognition</h2>
        </header>
        <section className="nav-panel">
          <nav className="panel nav-grid">
            <Link to="/">
              <button>Dashboard</button>
            </Link>
            <Link to="/games">
              <button>Games</button>
            </Link>
            <Link to="/pieces">
              <button>Pieces</button>
            </Link>
            <Link to="/mlimages">
              <button>ML Images</button>
            </Link>
            <Link to="/images">
              <button>Gallery</button>
            </Link>
            <Link to="/ml">
              <button>ML Capture</button>
            </Link>
            <Link to="/control">
              <button>Control</button>
            </Link>
          </nav>
        </section>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/games" element={<GamesManager />} />
            <Route path="/pieces" element={<PiecesManager />} />
            <Route path="/mlimages" element={<MLImagesManager />} />
            <Route
              path="/images"
              element={<ImageGallery gameId="dune_imperium" />}
            />
            <Route path="/ml" element={<ML />} />
            <Route path="/control" element={<Control />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
