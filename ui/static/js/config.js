/**
 * Frontend Configuration
 * This file is injected into the HTML during build to configure the API endpoint
 */

window.APP_CONFIG = {
  // API endpoint for transcription
  API_URL: window.location.hostname.includes('netlify.app') 
    ? 'https://speech-to-text-api.onrender.com'
    : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:7865'
    : window.location.origin,
  
  // Environment
  ENVIRONMENT: window.location.hostname.includes('netlify.app') 
    ? 'production'
    : 'development',
  
  // Debug mode
  DEBUG: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
};

// Log configuration for debugging
if (window.APP_CONFIG.DEBUG) {
  console.log('App Configuration:', window.APP_CONFIG);
}
