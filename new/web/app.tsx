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
