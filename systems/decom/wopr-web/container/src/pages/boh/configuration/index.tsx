import { Link } from "react-router-dom";
import { Outlet, NavLink } from 'react-router-dom';

export default function ConfigurationIndex() {

  return (
    <div className="Configuration">
      <nav className="secondary-nav" aria-label="Configuration">
        <ul>
          <li><NavLink to="woprconfig">WOPR Configuration</NavLink></li>
        </ul>
      </nav>
      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}