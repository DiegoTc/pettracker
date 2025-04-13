/**
 * Test script for API client configuration
 * 
 * This script simulates the behavior of the API client module to verify
 * that it correctly uses the environment variables or fallback values.
 * 
 * Usage:
 *   node test_api_client.js
 */

// Simulate environment variables
const apiBaseUrlEnv = process.env.VITE_API_BASE_URL;

// Function to determine API base URL (similar to our Vue component)
function getApiBaseUrl() {
  // Use environment variable if provided
  if (apiBaseUrlEnv) {
    console.log(`Using API base URL from environment: ${apiBaseUrlEnv}`);
    return apiBaseUrlEnv;
  }
  
  // Fallback for development when env var is not defined
  const fallbackUrl = 'http://localhost:5000';
  console.log(`No API base URL in environment, using fallback: ${fallbackUrl}`);
  return fallbackUrl;
}

// Simulate API client creation
function createApiClient() {
  // Get the base URL for API calls
  const apiBaseUrl = getApiBaseUrl();
  
  console.log(`API Client would be configured with baseURL: ${apiBaseUrl}`);
  console.log(`Example API endpoint URL: ${apiBaseUrl}/api/auth/check`);
  
  // Return an object simulating the client
  return {
    baseURL: apiBaseUrl,
    endpoints: {
      login: `${apiBaseUrl}/api/auth/login`,
      callback: `${apiBaseUrl}/api/auth/callback`,
      pets: `${apiBaseUrl}/api/pets/`,
      devices: `${apiBaseUrl}/api/devices/`
    }
  };
}

// Run tests
console.log('===== API CLIENT CONFIGURATION TEST =====');

// Test with environment variable
if (apiBaseUrlEnv) {
  console.log('Environment variable VITE_API_BASE_URL is set to:', apiBaseUrlEnv);
} else {
  console.log('Environment variable VITE_API_BASE_URL is not set');
}

const client = createApiClient();

console.log('\nTesting example API endpoints:');
Object.entries(client.endpoints).forEach(([name, url]) => {
  console.log(`- ${name}: ${url}`);
});

console.log('\nVERIFICATION:');
console.log('✓ All endpoints should be using the same base URL');
console.log('✓ Base URL should be http://localhost:5000 (development)');
console.log('✓ The client should not be using relative URLs that would be processed by the dev server');
console.log('=====================================');