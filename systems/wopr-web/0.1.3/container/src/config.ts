interface WoprConfig {
  apiUrl: string;
  camUrl: string;
  storageUrl: string;
}

const defaultConfig: WoprConfig = {
  apiUrl: "http://localhost:8000",
  camUrl: "http://localhost:5000",
  storageUrl: "http://localhost:8080/wopr",
};

export const config: WoprConfig = (window as any).woprConfig || defaultConfig;