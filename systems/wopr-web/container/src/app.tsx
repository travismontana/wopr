import { Routes, Route, Link } from "react-router-dom";
import "./pages/css/theme.css";

import Dashboard from "./pages/dashboard";
import Games from "./pages/games";
import Images from "./pages/images";
import ML from "./pages/ml"; 
import Control from "./pages/control"; 

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
            <Link to="/"><button>Dashboard</button></Link>
            <Link to="/games"><button>Games</button></Link>
            <Link to="/images"><button>Images</button></Link>
            <Link to="/ml"><button>ML</button></Link>
            <Link to="/control"><button>Control</button></Link>
          </nav>
        </section>
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/games" element={<Games />} />
            <Route path="/images" element={<Images />} />
            <Route path="/ml" element={<ML />} />
            <Route path="/control" element={<Control />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
