import { createContext, useContext } from "react";
import type { WoprConfig } from "./appConfig";

export const ConfigContext = createContext<WoprConfig | null>(null);

export function useConfig(): WoprConfig {
  const cfg = useContext(ConfigContext);
  if (!cfg) throw new Error("useConfig must be used within ConfigContext.Provider");
  return cfg;
}