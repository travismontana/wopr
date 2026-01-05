import React from "react";
import ReactDOM from "react-dom/client";
import { Routes } from "@generouted/react-router";

import { ConfigContext } from "@/config/ConfigContext";
import { fetchWoprConfig } from "@/config/fetchConfig";

import "./themes/modern.css";

async function bootstrap() {
  const config = await fetchWoprConfig();

  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      {/* ADDED: provide config to the whole app */}
      <ConfigContext.Provider value={Object.freeze(config)}>
        <Routes />
      </ConfigContext.Provider>
    </React.StrictMode>
  );
}

bootstrap().catch((err) => {
  console.error("[WOPR] failed to bootstrap config", err);
  document.body.innerHTML = "WOPR BOOT FAILURE: could not load config.";
});
