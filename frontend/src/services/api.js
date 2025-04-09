import axios from 'axios';

// Create an axios instance with the appropriate base URL
const apiClient = axios.create({
  // Always use the absolute backend URL when not working through the proxy
  baseURL: 'http://localhost:5000',
  // Important: withCredentials is needed for cookies/session to work across domains
  withCredentials: true
});

// Add a request interceptor to include JWT token in headers
apiClient.interceptors.request.use(
  (config) => {
    // Get the token from localStorage if it exists
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor for common error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response success:', response.config.method, response.config.url, response.status);
    return response;
  },
  (error) => {
    // Log detailed API error information
    console.error('API Response error:', 
      error.config?.method, 
      error.config?.url, 
      error.response?.status,
      error.response?.data || error.message
    );
    
    // You can add global error handling here
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  checkAuth: () => apiClient.get('/api/auth/check/'),
  logout: () => apiClient.post('/api/auth/logout/'),
  getUser: () => apiClient.get('/api/auth/user/'),
  getLoginInfo: () => apiClient.get('/api/auth/login_info/'),
  login: () => apiClient.get('/api/auth/login/'),
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