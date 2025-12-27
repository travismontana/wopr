import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

const apiUrl1 = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";

const apiUrl = `${apiUrl1}/api/v1`;

/*
Sample status data:
{"timestamp_right_before_data_pull":"2025-12-27T05:08:39.517291Z","db_up":true,"db_queriable":true,"db_writable":true,"wopr_web_up":false,"wopr_web_functional":false,"wopr_api_up":true,"wopr_api_functional":false,"wopr_cam_up":false,"wopr_cam_functional":false,"wopr_config_map_present":false,"timestamp_right_after_data_pull":"2025-12-27T05:08:39.670033Z"}
*/

export default function StatusPage() {
  const [statusData, setStatusData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${apiUrl}/status`);
      if (!response.ok) {
        throw new Error(`Error fetching status: ${response.statusText}`);
      }
      const data = await response.json();
      setStatusData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      setStatusData(null);
    }
    finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    intervalRef.current = setInterval(fetchStatus, 30000); // Refresh every 30 seconds
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  const statusItems = useMemo(() => {
    if (!statusData) return [];
    return Object.entries(statusData).map(([key, value]) => ({
      key,
      value: value === true ? "✅" : value === false ? "❌" : String(value),
    }));
  }, [statusData]);

  return (
    <div className="status-page">
      <h1>System Status</h1>
      {loading && <p>Loading status...</p>}
      {error && <p className="error">Error: {error}</p>}
      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Component</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {statusItems.map(({ key, value }) => (
              <tr key={key}>
                <td>{key}</td>
                <td>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}