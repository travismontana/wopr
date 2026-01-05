import type { WoprConfig } from "./appConfig";

//const directusurl = "https://directus.wopr.tailandtraillabs.org";
const directusurl = "https://api.wopr.tailandtraillabs.org";
const environment = "production";

export async function fetchWoprConfig(): Promise<WoprConfig> {
  const res = await fetch(`${directusurl}/api/v2/config/all?environment=${environment}`, {
    headers: { Accept: "application/json" },
  });

  if (!res.ok) throw new Error(`Config fetch failed: ${res.status}`);
  return res.json();
}
