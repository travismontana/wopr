const apiUrl1 = (window as any).ENV?.WOPR_API_URL || "http://wopr-api.wopr.svc:8000";
const apiUrl = `${apiUrl1}/api/v1`;

export { apiUrl };