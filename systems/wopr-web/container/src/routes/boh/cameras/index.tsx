import React, { useEffect, useMemo, useRef, useState } from "react";
import { Outlet, NavLink } from 'react-router-dom';

import { apiUrl } from "@lib/api";
export default function CameraPage() {
  return (
    <div className="camera">
      <nav className="secondary-nav" aria-label="Cameras">
        <ul>
          <li><NavLink to="capture">Capture</NavLink></li>
          <li><NavLink to="config">Configuration</NavLink></li>
          <li><NavLink to="status">Status</NavLink></li>
        </ul>
      </nav>
      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}