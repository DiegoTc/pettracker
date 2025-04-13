import axios from 'axios';

// Determine the API base URL based on environment
const getApiBaseUrl = () => {
  // Use environment variable if provided
  if (import.meta.env.VITE_API_BASE_URL) {
    console.log(`Using API base URL from environment: ${import.meta.env.VITE_API_BASE_URL}`);
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Fallback for development when env var is not defined
  const fallbackUrl = 'http://localhost:5000';
  console.log(`No API base URL in environment, using fallback: ${fallbackUrl}`);
  return fallbackUrl;
};

// Get the base URL for API calls
const apiBaseUrl = getApiBaseUrl();

// Create an axios instance with the appropriate base URL
const apiClient = axios.create({
  baseURL: apiBaseUrl,
  // Important: withCredentials is needed for cookies/session to work across domains
  withCredentials: true
});

// Log the configured base URL
console.log(`API Client configured with baseURL: ${apiBaseUrl}`);

// Log the full URL for a sample API endpoint
console.log(`Example API endpoint URL: ${apiBaseUrl}/api/auth/check`);

// Add a request interceptor to include JWT token in headers
apiClient.interceptors.request.use(
  (config) => {
    // Construct and log the full URL being called
    const fullUrl = `${config.baseURL || ''}${config.url}`;
    console.log(`Making API request to: ${config.method?.toUpperCase() || 'GET'} ${fullUrl}`);
    
    // Get the token from localStorage if it exists
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log(`Using auth token: ${token.substring(0, 15)}...`);
    } else {
      console.warn(`No authentication token available for request`);
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add a response interceptor for common error handling
apiClient.interceptors.response.use(
  (response) => {
    // Construct the full URL that was called
    const fullUrl = `${response.config.baseURL || ''}${response.config.url}`;
    console.log(`API Response success: ${response.config.method?.toUpperCase() || 'GET'} ${fullUrl} → ${response.status}`);
    return response;
  },
  (error) => {
    // Construct the full URL that was called
    const fullUrl = `${error.config?.baseURL || ''}${error.config?.url || ''}`;
    const method = error.config?.method?.toUpperCase() || 'GET';
    
    // Log detailed API error information
    console.error(`API Response error: ${method} ${fullUrl} → ${error.response?.status || 'Network Error'}`);
    console.error('Error details:', error.response?.data || error.message);
    
    // Handle authentication errors
    if (error.response?.status === 401) {
      console.warn('Authentication error detected, clearing tokens');
      localStorage.removeItem('access_token');
      localStorage.removeItem('is_authenticated');
      
      // If not already on the login page, redirect to login
      if (!window.location.pathname.includes('/login')) {
        // Store the current path for redirect after login
        localStorage.setItem('login_redirect', window.location.pathname);
        // Redirect to login
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  checkAuth: () => apiClient.get('/api/auth/check'),
  logout: () => apiClient.post('/api/auth/logout'),
  getUser: () => apiClient.get('/api/auth/user'),
  getLoginInfo: () => apiClient.get('/api/auth/login_info'),
  login: () => apiClient.get('/api/auth/login'),
};

// Pets API
export const petsAPI = {
  getAll: () => apiClient.get('/api/pets/'),
  getById: (id) => apiClient.get(`/api/pets/${id}/`),
  create: (petData) => apiClient.post('/api/pets/', petData),
  update: (id, petData) => apiClient.put(`/api/pets/${id}/`, petData),
  delete: (id) => apiClient.delete(`/api/pets/${id}/`),
};

// Devices API
export const devicesAPI = {
  getAll: () => apiClient.get('/api/devices/'),
  getById: (id) => apiClient.get(`/api/devices/${id}/`),
  create: (deviceData) => apiClient.post('/api/devices/', deviceData),
  update: (id, deviceData) => apiClient.put(`/api/devices/${id}/`, deviceData),
  delete: (id) => apiClient.delete(`/api/devices/${id}/`),
  assignToPet: (deviceId, petId) => apiClient.post(`/api/devices/${deviceId}/assign/${petId}/`),
  unassignFromPet: (deviceId) => apiClient.post(`/api/devices/${deviceId}/unassign/`),
  ping: (deviceId) => apiClient.post(`/api/devices/${deviceId}/ping/`),
};

// Locations API
export const locationsAPI = {
  getPetLocations: (petId) => apiClient.get(`/api/locations/pet/${petId}/`),
  getDeviceLocations: (deviceId) => apiClient.get(`/api/locations/device/${deviceId}/`),
  getPetLatestLocation: (petId) => apiClient.get(`/api/locations/pet/${petId}/latest/`),
  getDeviceLatestLocation: (deviceId) => apiClient.get(`/api/locations/device/${deviceId}/latest/`),
  getAllPetsLatestLocations: () => apiClient.get('/api/locations/all-pets-latest/'),
  getRecent: (limit = 10) => apiClient.get(`/api/locations/recent/?limit=${limit}`),
  recordLocation: (locationData) => apiClient.post('/api/locations/record/', locationData),
  simulateLocation: (locationData) => apiClient.post('/api/locations/simulate/', locationData),
};

export default apiClient;