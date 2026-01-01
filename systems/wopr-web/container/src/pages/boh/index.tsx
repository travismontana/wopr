import { Link } from "react-router-dom";

export default function BackOfHouseIndex() {
  return (
    <div className="panel">
      <h1>Back of House</h1>
      <p>WOPR System Administration</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/ml">ML</Link> - Machine Learning image capture and training data management</li>
          <li><Link to="/boh/inventory">Inventory</Link> - Game pieces, cameras, and equipment management</li>
          <li><Link to="/boh/configuration">Configuration</Link> - System configuration and settings</li>
          <li><Link to="/boh/status">Status</Link> - System health and monitoring</li>
        </ul>
      </nav>
    </div>
  );
}