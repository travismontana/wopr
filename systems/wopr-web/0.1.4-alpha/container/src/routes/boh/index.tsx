import { Outlet, NavLink } from "react-router-dom";

export default function BackOfHouse() {
  return (
    <div className="boh">
      <nav className="secondary-nav" aria-label="Back of House">
        <ul>
          <li><NavLink to="/boh/ml">Machine Learning</NavLink></li>
          <li><NavLink to="/boh/cameras">Cameras</NavLink></li>
          <li><NavLink to="/boh/images">Images</NavLink></li>
          <li><NavLink to="/boh/config">Configuration</NavLink></li>
          <li><NavLink to="/boh/status">Status</NavLink></li>
        </ul>
      </nav>
      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}