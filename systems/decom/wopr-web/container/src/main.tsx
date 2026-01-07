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
