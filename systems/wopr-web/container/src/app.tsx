import { Routes, Route, Link } from "react-router-dom";
import "./css/theme.css";

import Dashboard from "./pages/Dashboard";
import Games from "./pages/Games";
import Images from "./pages/Images";
import MLHome from "./pages/MLHome";
import MLPieces from "./pages/MLPieces";
import MLLabel from "./pages/MLLabel";
import MLDatasets from "./pages/MLDatasets";
import MLTrain from "./pages/MLTrain";

export default function App() {
  return (
    <div className="app">
      <div className="layout">
        <header className="wopr-header">
          <h1>WOPR</h1>
          <h2>Wargaming Oversight &amp; Position Recognition</h2>
        </header>

        <section className="camera-panel">
          <h1>Camera Controls</h1>
          <div className="actions">
            <button>Capture</button>
            <button>View</button>
            <button>Confirm</button>
          </div>
        </section>

        <section className="control-panel">
          <h1>Control Controls</h1>
          <div className="actions">
            <button>Edit wopr configs</button>
          </div>
        </section>

        <section className="nav-panel">
          <nav className="nav">
            <Link to="/">Dashboard</Link> |{" "}
            <Link to="/games">Games</Link> |{" "}
            <Link to="/images">Images</Link> |{" "}
            <Link to="/ml">ML</Link>
          </nav>
        </section>

        <main className="page">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/games" element={<Games />} />
            <Route path="/images" element={<Images />} />

            <Route path="/ml" element={<MLHome />} />
            <Route path="/ml/pieces" element={<MLPieces />} />
            <Route path="/ml/label" element={<MLLabel />} />
            <Route path="/ml/datasets" element={<MLDatasets />} />
            <Route path="/ml/train" element={<MLTrain />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
