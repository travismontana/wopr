const apiUrl = (window as any).ENV?.WOPR_API_URL || "https://api.wopr.tailandtraillabs.org";
const apiUrlFull = `${apiUrl}/api/v1`;

export { apiUrl, apiUrlFull };