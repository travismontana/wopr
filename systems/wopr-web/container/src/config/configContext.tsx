import { createContext, useContext } from "react";
import type { WoprConfig } from "./appConfig";

export const configContext = createContext<WoprConfig | null>(null);

export function useConfig(): WoprConfig {
  const cfg = useContext(configContext);
  if (!cfg) throw new Error("useConfig must be used within ConfigContext.Provider");
  return cfg;
}