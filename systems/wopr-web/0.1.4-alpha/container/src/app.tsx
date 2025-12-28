import { Outlet, NavLink } from "react-router-dom";
// Theme
import "./themes/modern.css";

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
          <li><NavLink to="/settings">Settings</NavLink></li>
        </ul>
      </nav>

      <main className="content" role="main">
        <Outlet />
      </main>

      <footer className="system-status" role="contentinfo">
        <span className="status-indicator" data-status="operational">SYS:OK</span>
        <span className="version">v{import.meta.env.WOPR_VERSION || '0.0.0'}</span>
      </footer>
    </div>
  );
}