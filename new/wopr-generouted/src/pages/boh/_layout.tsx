/**
 * Copyright 2026 Bob Bomar
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { Outlet, NavLink } from "react-router-dom";

export default function BackOfHouse() {
  return (
    <div className="boh">
      <nav className="secondary-nav" aria-label="Back of House">
        <ul>
          <li><NavLink to="/boh/games">Games Manager</NavLink></li>
          <li><NavLink to="/boh/pieces">Pieces Manager</NavLink></li>
          <li><NavLink to="/boh/mlimages">Machine Learning Images Manager</NavLink></li>
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
