import axios from 'axios';

// Determine if this is running in development mode (on localhost/127.0.0.1)
const isDevelopment = window.location.hostname === 'localhost' || 
                     window.location.hostname === '127.0.0.1';

// Create an axios instance with the base URL from environment variable
// In development mode, we don't need the base URL since the Vite proxy will handle it
const apiClient = axios.create({
  baseURL: isDevelopment ? '' : (import.meta.env.VITE_API_BASE_URL || ''),
});

// Add a request interceptor for common headers
apiClient.interceptors.request.use(
  (config) => {
    // You can add common headers here if needed (e.g., authorization)
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for common error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // You can add global error handling here
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
  getAll: () => apiClient.get('/api/pets'),
  getById: (id) => apiClient.get(`/api/pets/${id}`),
  create: (petData) => apiClient.post('/api/pets', petData),
  update: (id, petData) => apiClient.put(`/api/pets/${id}`, petData),
  delete: (id) => apiClient.delete(`/api/pets/${id}`),
};

// Devices API
export const devicesAPI = {
  getAll: () => apiClient.get('/api/devices'),
  getById: (id) => apiClient.get(`/api/devices/${id}`),
  create: (deviceData) => apiClient.post('/api/devices', deviceData),
  update: (id, deviceData) => apiClient.put(`/api/devices/${id}`, deviceData),
  delete: (id) => apiClient.delete(`/api/devices/${id}`),
  assignToPet: (deviceId, petId) => apiClient.post(`/api/devices/${deviceId}/assign/${petId}`),
  unassignFromPet: (deviceId) => apiClient.post(`/api/devices/${deviceId}/unassign`),
  ping: (deviceId) => apiClient.post(`/api/devices/${deviceId}/ping`),
};

// Locations API
export const locationsAPI = {
  getPetLocations: (petId) => apiClient.get(`/api/locations/pet/${petId}`),
  getDeviceLocations: (deviceId) => apiClient.get(`/api/locations/device/${deviceId}`),
  getPetLatestLocation: (petId) => apiClient.get(`/api/locations/latest/pet/${petId}`),
  getDeviceLatestLocation: (deviceId) => apiClient.get(`/api/locations/latest/device/${deviceId}`),
  getAllPetsLatestLocations: () => apiClient.get('/api/locations/all-pets-latest'),
  getRecent: (limit = 10) => apiClient.get(`/api/locations/recent?limit=${limit}`),
  recordLocation: (locationData) => apiClient.post('/api/locations/record', locationData),
  simulateLocation: (locationData) => apiClient.post('/api/locations/simulate', locationData),
};

export default apiClient;