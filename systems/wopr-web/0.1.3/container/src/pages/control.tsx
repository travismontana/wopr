import { Routes, Route, Link } from "react-router-dom";
import "./css/theme.css";

const apiUrl1 = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";
const apiUrl = `${apiUrl1}/api/v1`;


export default function control() {
  return (
    <section className="control-panel">
        <h1>Control Controls</h1>
        <div className="actions">
          <button>Edit wopr configs</button>
        </div>
    </section>
  );
}
