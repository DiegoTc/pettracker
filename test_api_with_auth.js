/**
 * API endpoint tester with authentication for PetTracker
 * This script tests the API endpoints for pets and devices with authentication
 */

// Set up API base URL - change this to match your environment
const API_BASE_URL = 'http://localhost:5000';

// Mock credentials for testing
const EMAIL = 'test@example.com';
const PASSWORD = 'password123';

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
      data,
      headers: Object.fromEntries(response.headers.entries())
    };
  } catch (error) {
    console.error(`Network error for ${url}:`, error);
    return { ok: false, error: error.message };
  }
}

// Login to get an auth token
async function login() {
  const loginResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/auth/login_with_password`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email: EMAIL, password: PASSWORD }),
  });
  
  console.log('Login response:', loginResponse);
  
  if (loginResponse.ok && loginResponse.data && loginResponse.data.token) {
    console.log('Login successful!');
    return loginResponse.data.token;
  } else {
    console.log('Login failed, will try to use login_info');
    
    // Try to get login_info to see what options are available
    const loginInfoResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/auth/login_info`);
    console.log('Login info response:', loginInfoResponse);
    
    throw new Error('Authentication failed. Check your credentials or login method.');
  }
}

// Test specific endpoints
async function testEndpointsWithAuth() {
  console.log('=== Testing PetTracker API Endpoints With Auth ===');
  
  try {
    // Try to login or check auth status
    let token;
    try {
      token = await login();
    } catch (err) {
      console.log('Could not authenticate:', err.message);
      
      // Switch to check only authentication-free endpoints
      console.log('\n--- Testing public endpoints ---');
      
      // Test /api/auth/login_info endpoint
      const loginInfoResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/auth/login_info`);
      console.log('Login Info Response:', loginInfoResponse.data);
      
      // Test /api/auth/check endpoint
      const checkResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/auth/check`);
      console.log('Auth Check Response:', checkResponse.data);
      
      // Test a non-existent endpoint to see how it handles 404
      const notFoundResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/nonexistent`);
      console.log('Non-existent endpoint response:', notFoundResponse);
      
      // End testing without auth
      return;
    }
    
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
    
    // Test pet endpoints
    console.log('\n--- Testing Pet Endpoints ---');
    
    // List all pets
    const allPets = await fetchWithErrorHandling(`${API_BASE_URL}/api/pets/`, { headers });
    console.log('All Pets Response:', allPets.data);
    
    if (allPets.data && allPets.data.length > 0) {
      const petId = allPets.data[0].id;
      
      // Test pet with trailing slash
      console.log(`\nGetting pet ${petId} with trailing slash`);
      const petWithSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/pets/${petId}/`, { headers });
      console.log(`Status: ${petWithSlash.status}`);
      console.log('Response Data:', petWithSlash.data);
      
      // Test pet without trailing slash
      console.log(`\nGetting pet ${petId} without trailing slash`);
      const petWithoutSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/pets/${petId}`, { headers });
      console.log(`Status: ${petWithoutSlash.status}`);
      console.log('Response Data:', petWithoutSlash.data);
    }
    
    // Test device endpoints
    console.log('\n--- Testing Device Endpoints ---');
    
    // List all devices
    const allDevices = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/`, { headers });
    console.log('All Devices Response:', allDevices.data);
    
    if (allDevices.data && allDevices.data.length > 0) {
      const deviceId = allDevices.data[0].id;
      
      // Test device with trailing slash
      console.log(`\nGetting device ${deviceId} with trailing slash`);
      const deviceWithSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/${deviceId}/`, { headers });
      console.log(`Status: ${deviceWithSlash.status}`);
      console.log('Response Data:', deviceWithSlash.data);
      
      // Test device without trailing slash
      console.log(`\nGetting device ${deviceId} without trailing slash`);
      const deviceWithoutSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/${deviceId}`, { headers });
      console.log(`Status: ${deviceWithoutSlash.status}`);
      console.log('Response Data:', deviceWithoutSlash.data);
    }
    
  } catch (error) {
    console.error('Error in test execution:', error);
  }
}

// Run the tests
testEndpointsWithAuth().catch(console.error);