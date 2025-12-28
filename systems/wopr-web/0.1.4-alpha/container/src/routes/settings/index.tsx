import { Outlet, NavLink } from "react-router-dom";

export default function Settings() {
  return (
    <div className="settings">
      <nav className="secondary-nav" aria-label="Settings">
        <ul>
          <li><NavLink to="/settings/ml">Machine Learning</NavLink></li>
          <li><NavLink to="/settings/cameras">Cameras</NavLink></li>
          <li><NavLink to="/settings/config">Configuration</NavLink></li>
        </ul>
      </nav>
      <div className="settings-content">
        <Outlet />
      </div>
    </div>
  );
}