import { Routes, Route, Link } from "react-router-dom";
import "./css/theme.css";


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
