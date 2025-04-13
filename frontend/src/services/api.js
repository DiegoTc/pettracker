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
  /**
   * Check if the user is authenticated
   * @returns {Promise} Promise with authentication status
   */
  checkAuth: () => apiClient.get('/api/auth/check'),
  
  /**
   * Logout the current user
   * This will invalidate the session and JWT token
   * @returns {Promise} Promise with logout result
   */
  logout: async () => {
    try {
      // Generate a unique request ID for tracking this logout operation
      const requestId = `logout-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      
      // Add the request ID to the headers for server-side tracking
      return await apiClient.post('/api/auth/logout', {}, {
        headers: {
          'X-Request-ID': requestId
        }
      });
    } catch (error) {
      console.error('Logout API error:', error);
      // Re-throw the error to be handled by the calling component
      throw error;
    }
  },
  
  /**
   * Get current user information
   * @returns {Promise} Promise with user data
   */
  getUser: () => apiClient.get('/api/auth/user'),
  
  /**
   * Get login configuration information
   * @returns {Promise} Promise with login configuration
   */
  getLoginInfo: () => apiClient.get('/api/auth/login_info'),
  
  /**
   * Initiate Google OAuth login flow
   * @returns {Promise} Promise that redirects to Google
   */
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

// Dashboard API
export const dashboardAPI = {
  /**
   * Get dashboard statistics (pets count, devices count, locations count)
   * @returns {Promise} Promise with dashboard stats
   */
  getStats: async () => {
    try {
      // Fetch pets count
      const petsResponse = await petsAPI.getAll();
      const petsCount = petsResponse.data.length;
      
      // Fetch devices count
      const devicesResponse = await devicesAPI.getAll();
      const devicesData = devicesResponse.data;
      const devicesCount = devicesData.length;
      
      // Count active devices
      const activeDevicesCount = devicesData.filter(device => device.is_active).length;
      
      // Fetch recent locations (if available)
      let locationsCount = 0;
      let activityScore = null;
      
      try {
        const locationsResponse = await locationsAPI.getRecent(100);
        locationsCount = locationsResponse.data.length;
        
        // Calculate a simple activity score (if locations exist)
        if (locationsCount > 0) {
          // Activity score formula could be based on recency and frequency
          // For now, just a placeholder that scales with location count (0-100)
          activityScore = Math.min(Math.floor(locationsCount * 5), 100);
        }
      } catch (error) {
        console.warn('Could not fetch locations count:', error);
        // Will return 0 for locations count
      }
      
      return {
        totalPets: petsCount,
        totalDevices: devicesCount,
        activeDevices: activeDevicesCount,
        totalLocations: locationsCount,
        activityScore: activityScore
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },
  
  /**
   * Get recent activities by combining location updates and other events
   * @param {Number} limit Maximum number of activities to return
   * @returns {Promise} Promise with recent activities
   */
  getRecentActivities: async (limit = 5) => {
    try {
      // Fetch recent locations
      const locationsResponse = await locationsAPI.getRecent(limit);
      const recentLocations = locationsResponse.data;
      
      // Transform locations into activity items
      const activities = await Promise.all(recentLocations.map(async location => {
        // Get device information
        let deviceInfo = null;
        try {
          const deviceResponse = await devicesAPI.getById(location.device_id);
          deviceInfo = deviceResponse.data;
        } catch (error) {
          console.warn(`Could not fetch device info for device ${location.device_id}:`, error);
        }
        
        // Get pet information if device is assigned to a pet
        let petInfo = null;
        if (deviceInfo && deviceInfo.pet_id) {
          try {
            const petResponse = await petsAPI.getById(deviceInfo.pet_id);
            petInfo = petResponse.data;
          } catch (error) {
            console.warn(`Could not fetch pet info for pet ${deviceInfo.pet_id}:`, error);
          }
        }
        
        // Calculate time ago string
        const locationTime = new Date(location.timestamp);
        const now = new Date();
        const diffMs = now - locationTime;
        const diffMinutes = Math.floor(diffMs / 60000);
        
        let timeAgo;
        if (diffMinutes < 1) {
          timeAgo = 'Just now';
        } else if (diffMinutes < 60) {
          timeAgo = `${diffMinutes} min ago`;
        } else if (diffMinutes < 1440) {
          const hours = Math.floor(diffMinutes / 60);
          timeAgo = `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
          const days = Math.floor(diffMinutes / 1440);
          timeAgo = `${days} day${days > 1 ? 's' : ''} ago`;
        }
        
        return {
          petName: petInfo ? petInfo.name : (deviceInfo ? deviceInfo.name : 'Unknown'),
          location: 'GPS Location',  // Placeholder - could be geocoded in the future
          timeAgo: timeAgo,
          batteryLevel: location.battery_level || 0,
          speed: location.speed || 0
        };
      }));
      
      return activities;
    } catch (error) {
      console.error('Error fetching recent activities:', error);
      // Instead of throwing, return empty array
      return [];
    }
  }
};

export default apiClient;