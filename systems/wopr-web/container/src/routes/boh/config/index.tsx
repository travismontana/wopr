import React, { useEffect, useMemo, useRef, useState } from "react";
import { Outlet, NavLink } from 'react-router-dom';

import { apiUrl } from "@lib/api";
export default function ConfigPage() {
  return (
    <div className="Config">
      <nav className="secondary-nav" aria-label="Config">
        <ul>
          <li><NavLink to="control">Control</NavLink></li>
          <li><NavLink to="edit">Edit</NavLink></li>
          <li><NavLink to="other">Other</NavLink></li>
        </ul>
      </nav>
      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}