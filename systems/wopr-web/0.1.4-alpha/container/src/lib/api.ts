const apiUrl1 = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";
const apiUrl = `${apiUrl1}/api/v1`;

export { apiUrl };