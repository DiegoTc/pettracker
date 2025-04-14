/**
 * Test script to simulate a device edit form submission
 * This will help verify if the frontend properly calls the API endpoints
 */

const API_BASE_URL = 'http://localhost:5000';

// Utility function to generate a random device ID
function generateDeviceId() {
  const prefix = 'PT';
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = prefix;
  for (let i = 0; i < 8; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Fetch with error handling
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

// Test device form endpoints
async function testDeviceForm() {
  console.log('=== Testing Device Form API Interactions ===');
  
  // First try to verify URL handling
  console.log('\n--- Testing Frontend Routes ---');
  
  // Access the device edit page path
  const deviceEditPage = await fetchWithErrorHandling(`${API_BASE_URL}/devices/edit/1`);
  console.log(`Frontend route status: ${deviceEditPage.status}`);
  if (deviceEditPage.type === 'text') {
    // Check if we're getting HTML (correct) or JSON (API endpoint incorrectly handling)
    console.log(`Response starts with: ${deviceEditPage.text.substring(0, 100)}...`);
    
    // Check for indicators that we got the right response
    const isHtml = deviceEditPage.text.includes('<!DOCTYPE html>') || 
                  deviceEditPage.text.includes('<html') ||
                  deviceEditPage.text.includes('<head');
    
    console.log(`Response appears to be HTML: ${isHtml}`);
  } else {
    console.log('Unexpected response type:', deviceEditPage.type);
    console.log('Response data:', deviceEditPage.data);
  }
  
  // Test API path with only the ID (no trailing slash)
  console.log('\n--- Testing API path with ID only ---');
  const apiPathNoSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/1`);
  console.log(`API path no slash status: ${apiPathNoSlash.status}`);
  console.log('Response type:', apiPathNoSlash.type);
  if (apiPathNoSlash.type === 'json') {
    // This is correct - we should get a JSON response with 401 if not authenticated
    console.log('API correctly returning JSON for /api/devices/1');
  } else {
    console.log('API returning non-JSON response for /api/devices/1:');
    console.log(apiPathNoSlash.text || apiPathNoSlash.data);
  }
  
  // Test API path with trailing slash
  console.log('\n--- Testing API path with trailing slash ---');
  const apiPathWithSlash = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/1/`);
  console.log(`API path with slash status: ${apiPathWithSlash.status}`);
  console.log('Response type:', apiPathWithSlash.type);
  if (apiPathWithSlash.type === 'json') {
    // This is correct - we should get a JSON response with 401 if not authenticated
    console.log('API correctly returning JSON for /api/devices/1/');
  } else {
    console.log('API returning non-JSON response for /api/devices/1/:');
    console.log(apiPathWithSlash.text || apiPathWithSlash.data);
  }
  
  // Create a device to edit - this will fail without authentication, but that's expected
  // The purpose is to see if the URL is correctly routed
  console.log('\n--- Attempting to create a device (expected to fail with 401) ---');
  const newDevice = {
    name: 'Test Device',
    device_id: generateDeviceId(),
    device_type: '808_tracker',
    is_active: true
  };
  
  const createResponse = await fetchWithErrorHandling(`${API_BASE_URL}/api/devices/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(newDevice)
  });
  
  console.log(`Create response status: ${createResponse.status}`);
  console.log('Response type:', createResponse.type);
  if (createResponse.type === 'json') {
    console.log('API correctly handling device creation endpoint');
    if (createResponse.status === 401) {
      console.log('Authentication required, as expected');
    } else {
      console.log('Unexpected status code for unauthenticated request:', createResponse.status);
    }
  } else {
    console.log('API returning non-JSON response for device creation:');
    console.log(createResponse.text || createResponse.data);
  }
}

// Run the test
testDeviceForm().catch(console.error);