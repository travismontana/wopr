import { Link } from "react-router-dom";

export default function ConfigurationIndex() {
  return (
    <div className="panel">
      <h1>Configuration</h1>
      <p>System settings and configuration</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/config">System Configuration</Link> - View and modify system settings</li>
        </ul>
      </nav>
    </div>
  );
}