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

export default function InventoryIndex() {
  return (
    <div className="panel">
      <h1>Inventory</h1>
      <p>Equipment and game piece management</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/games">Game Management</Link> - Manage game catalog and definitions</li>
          <li><Link to="/boh/pieces">Piece Management</Link> - Manage game pieces and components</li>
          <li><Link to="/boh/cameras">Camera Management</Link> - Configure and test cameras</li>
          <li><Link to="/boh/homeauto">Light Controls</Link> - Home automation and lighting settings</li>
        </ul>
      </nav>
    </div>
  );
}