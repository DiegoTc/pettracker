// Simple test script to diagnose edit form issues
const axios = require('axios');

// Test configuration
const API_BASE_URL = 'http://localhost:5000';
const TEST_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsImV4cCI6MTcxMzA2NDgwMH0.D-Wg2gwuL-hxTvzIKG8_QwJ7SN2NRkiP1OEiWZQhU3g'; // Replace with your development token

// Create an axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${TEST_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Test function to fetch a device by ID
async function testGetDevice(id) {
  try {
    console.log(`Fetching device with ID: ${id}`);
    const response = await api.get(`/api/devices/${id}/`);
    console.log('Response status:', response.status);
    console.log('Response data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching device:');
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    } else {
      console.error(error.message);
    }
    return null;
  }
}

// Test function to fetch a pet by ID
async function testGetPet(id) {
  try {
    console.log(`Fetching pet with ID: ${id}`);
    const response = await api.get(`/api/pets/${id}/`);
    console.log('Response status:', response.status);
    console.log('Response data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching pet:');
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    } else {
      console.error(error.message);
    }
    return null;
  }
}

// Run tests
async function runTests() {
  console.log('Testing device API endpoint...');
  await testGetDevice(1);
  
  console.log('\nTesting pet API endpoint...');
  await testGetPet(1);
}

// Start tests
runTests();