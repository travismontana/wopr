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

import { Link } from "react-router-dom";

export default function BackOfHouseIndex() {
  return (
    <div className="panel">
      <h1>Back of House</h1>
      <p>WOPR System Administration</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/ml">ML</Link> - Machine Learning image capture and training data management</li>
          <li><Link to="/boh/inventory">Inventory</Link> - Game pieces, cameras, and equipment management</li>
          <li><Link to="/boh/configuration">Configuration</Link> - System configuration and settings</li>
          <li><Link to="/boh/status">Status</Link> - System health and monitoring</li>
        </ul>
      </nav>
    </div>
  );
}