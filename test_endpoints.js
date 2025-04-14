/**
 * Simple endpoint tester script for PetTracker API
 * This script tests the API endpoints for fetching pet and device details
 * with both trailing and non-trailing slashes
 */

// Set up API base URL - change this to match your environment
const API_BASE_URL = 'http://localhost:5000';

// Fetch function with error handling
async function fetchWithErrorHandling(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const text = await response.text();
    let data;
    
    try {
      // Try to parse as JSON
      data = JSON.parse(text);
    } catch (e) {
      // If not valid JSON, just return the text
      console.log(`Response is not valid JSON: ${text.substring(0, 150)}...`);
      return { 
        ok: response.ok, 
        status: response.status, 
        type: 'text',
        text: text.substring(0, 200) + (text.length > 200 ? '...(truncated)' : '') 
      };
    }
    
    // Return structured response
    return { 
      ok: response.ok, 
      status: response.status, 
      type: 'json',
      data 
    };
  } catch (error) {
    console.error(`Network error for ${url}:`, error);
    return { ok: false, error: error.message };
  }
}

// Test specific endpoints
async function testEndpoints() {
  console.log('=== Testing PetTracker API Endpoints ===');
  
  // Test authentication first
  const headers = {
    'Content-Type': 'application/json',
  };
  
  // Test pet endpoint with trailing slash
  console.log('\n--- Testing Pet Endpoint (with trailing slash) ---');
  const petWithSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/pets/1/`, { headers });
  console.log(`Status: ${petWithSlash.status}`);
  console.log('Response Type:', petWithSlash.type);
  if (petWithSlash.type === 'json') {
    console.log('Response Data:', petWithSlash.data);
  } else {
    console.log('Response Text:', petWithSlash.text);
  }
  
  // Test pet endpoint without trailing slash
  console.log('\n--- Testing Pet Endpoint (without trailing slash) ---');
  const petWithoutSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/pets/1`, { headers });
  console.log(`Status: ${petWithoutSlash.status}`);
  console.log('Response Type:', petWithoutSlash.type);
  if (petWithoutSlash.type === 'json') {
    console.log('Response Data:', petWithoutSlash.data);
  } else {
    console.log('Response Text:', petWithoutSlash.text);
  }
  
  // Test device endpoint with trailing slash
  console.log('\n--- Testing Device Endpoint (with trailing slash) ---');
  const deviceWithSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/1/`, { headers });
  console.log(`Status: ${deviceWithSlash.status}`);
  console.log('Response Type:', deviceWithSlash.type);
  if (deviceWithSlash.type === 'json') {
    console.log('Response Data:', deviceWithSlash.data);
  } else {
    console.log('Response Text:', deviceWithSlash.text);
  }
  
  // Test device endpoint without trailing slash
  console.log('\n--- Testing Device Endpoint (without trailing slash) ---');
  const deviceWithoutSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/1`, { headers });
  console.log(`Status: ${deviceWithoutSlash.status}`);
  console.log('Response Type:', deviceWithoutSlash.type);
  if (deviceWithoutSlash.type === 'json') {
    console.log('Response Data:', deviceWithoutSlash.data);
  } else {
    console.log('Response Text:', deviceWithoutSlash.text);
  }
}

// Run the tests
testEndpoints().catch(console.error);