import React, { useEffect, useMemo, useRef, useState } from "react";
import { Outlet, NavLink } from 'react-router-dom';

import { apiUrl } from "@lib/api";

export default function ImagesPage() {
  return (
    <div className="Images">
      <nav className="secondary-nav" aria-label="Imagess">
        <ul>
          <li><NavLink to="view">View</NavLink></li>
          <li><NavLink to="gallery">Gallery</NavLink></li>
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