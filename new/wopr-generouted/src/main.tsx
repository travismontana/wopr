import React from "react";
import ReactDOM from "react-dom/client";
import { Routes } from "@generouted/react-router";

// Theme
import "./themes/modern.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Routes />
  </React.StrictMode>
);
