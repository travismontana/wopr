import { Outlet, NavLink } from "react-router-dom";

export default function CamerasLayout() {
  return (
    <div className="camera">
      <nav className="secondary-nav" aria-label="Cameras">
        <ul>
          <li><NavLink to="/boh/cameras/capture">Capture</NavLink></li>
          <li><NavLink to="/boh/cameras/config">Configuration</NavLink></li>
          <li><NavLink to="/boh/cameras/status">Status</NavLink></li>
        </ul>
      </nav>
      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}
