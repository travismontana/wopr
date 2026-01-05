/*
 * New caputre page.
 * things to know:
 * Directus url: 
 *
 */

import { useConfig } from "@/config/ConfigContext";

export default function Home() {
  const cfg = useConfig();
  return (
    <div>
      <h1>WOPR</h1>
      <pre>{JSON.stringify(cfg, null, 2)}</pre>
    </div>
  );
}