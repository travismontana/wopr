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
      {/* Breadcrumbs and Navigation Controls */}
      <div className="boh-header" style={{ 
        padding: '1rem', 
        borderBottom: '1px solid #374151',
        marginBottom: '1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <nav aria-label="Breadcrumb">
          <ol style={{ display: 'flex', gap: '0.5rem', listStyle: 'none', padding: 0, margin: 0 }}>
            {breadcrumbs.map((crumb, index) => (
              <li key={crumb.path} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {index > 0 && <span className="text-gray-500">/</span>}
                {index === breadcrumbs.length - 1 ? (
                  <span className="text-green-500 font-medium">{crumb.label}</span>
                ) : (
                  <Link to={crumb.path} className="text-gray-400 hover:text-green-500">
                    {crumb.label}
                  </Link>
                )}
              </li>
            ))}
          </ol>
        </nav>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {location.pathname !== '/boh' && (
            <>
              <button 
                onClick={handleBack}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
              >
                ← Back
              </button>
              <button 
                onClick={handleHome}
                className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm"
              >
                🏠 Home
              </button>
            </>
          )}
        </div>
      </div>

      <div className="boh-content">
        <Outlet />
      </div>
    </div>
  );
}