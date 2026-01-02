// Keep your existing api.ts file - this is just showing the structure

export const apiUrl = 
  (window as any).ENV?.WOPR_API_URL || 
  "https://wopr-api.studio.abode.tailandtraillabs.org";

// Add any other API utilities here
