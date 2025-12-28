import React, { useEffect, useMemo, useRef, useState } from "react";

import { apiUrl } from "@lib/api";
export default function CameraPage() {
  return (
    <div className="camera">
      <nav className="secondary-nav" aria-label="Settings">
        <ul>
          <li><NavLink to="/cameras/capture">Machine Learning</NavLink></li
          <li><NavLink to="/cameras/config">Configuration</NavLink></li>
          <li><NavLink to="/cameras/status">Status</NavLink></li>
        </ul>
      </nav>
      <div className="settings-content">
        <Outlet />
      </div>
    </div>
  );
}