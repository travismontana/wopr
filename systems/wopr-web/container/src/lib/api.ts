const apiUrl = (window as any).ENV?.WOPR_API_URL || "http://wopr-api.wopr.svc:8000";
const apiUrlFull = `${apiUrl}/api/v1`;

export { apiUrl, apiUrlFull };