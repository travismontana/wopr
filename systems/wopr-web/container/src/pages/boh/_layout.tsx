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