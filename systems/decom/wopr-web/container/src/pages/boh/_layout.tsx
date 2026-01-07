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

import { Outlet, useLocation, useNavigate, Link } from "react-router-dom";

export default function BackOfHouse() {
  const location = useLocation();
  const navigate = useNavigate();

  // Build breadcrumb trail from path
  const pathSegments = location.pathname.split('/').filter(Boolean);
  const breadcrumbs = pathSegments.map((segment, index) => {
    const path = '/' + pathSegments.slice(0, index + 1).join('/');
    const label = segment.charAt(0).toUpperCase() + segment.slice(1);
    return { path, label };
  });

  const handleBack = () => {
    navigate(-1);
  };

  const handleHome = () => {
    navigate('/boh');
  };

  return (
    <div className="boh">
      <div className="toolbar">
        <div>
          {breadcrumbs.map((crumb, index) => (
            <span key={crumb.path}>
              {index > 0 && <span> / </span>}
              {index === breadcrumbs.length - 1 ? (
                <span>{crumb.label}</span>
              ) : (
                <Link to={crumb.path}>{crumb.label}</Link>
              )}
            </span>
          ))}
        </div>

        {location.pathname !== '/boh' && (
          <div className="actions">
            <button onClick={handleBack}>← Back</button>
            <button onClick={handleHome}>🏠 Home</button>
          </div>
        )}
      </div>

      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}