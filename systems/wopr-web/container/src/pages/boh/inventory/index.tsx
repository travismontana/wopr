import { Link } from "react-router-dom";

export default function InventoryIndex() {
  return (
    <div className="panel">
      <h1>Inventory</h1>
      <p>Equipment and game piece management</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/games">Game Management</Link> - Manage game catalog and definitions</li>
          <li><Link to="/boh/pieces">Piece Management</Link> - Manage game pieces and components</li>
          <li><Link to="/boh/cameras">Camera Management</Link> - Configure and test cameras</li>
          <li><Link to="/boh/homeauto">Light Controls</Link> - Home automation and lighting settings</li>
        </ul>
      </nav>
    </div>
  );
}