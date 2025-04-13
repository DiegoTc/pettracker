<template>
  <div class="api-test-container">
    <h1 class="page-title">API Test Page</h1>
    
    <div class="card mb-4">
      <div class="card-header">
        <h2>API Configuration</h2>
      </div>
      <div class="card-body">
        <div class="mb-3">
          <label class="form-label">API Base URL (Current)</label>
          <div class="input-group">
            <input type="text" class="form-control" v-model="apiBaseUrl" :disabled="!editingBaseUrl" />
            <button class="btn btn-outline-secondary" @click="toggleEditBaseUrl">
              {{ editingBaseUrl ? 'Save' : 'Edit' }}
            </button>
          </div>
          <small class="form-text text-muted mt-1">
            This overrides the environment variable for this session only.
          </small>
        </div>
        
        <div class="mb-3">
          <label class="form-label">Environment Variables</label>
          <div class="alert alert-info">
            <p><strong>VITE_API_BASE_URL:</strong> {{ envApiBaseUrl || 'Not set' }}</p>
          </div>
        </div>
        
        <div class="mb-3">
          <label class="form-label">Quick URLs</label>
          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-sm btn-outline-primary" @click="setApiBaseUrl('http://localhost:5000')">
              localhost:5000 (Flask)
            </button>
            <button class="btn btn-sm btn-outline-primary" @click="setApiBaseUrl(window.location.origin)">
              {{ window.location.origin }} (Current Origin)
            </button>
            <button class="btn btn-sm btn-outline-secondary" @click="setApiBaseUrl('https://api.pettracker.com')">
              api.pettracker.com (Production)
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card mb-4">
      <div class="card-header">
        <h2>Authentication Status</h2>
      </div>
      <div class="card-body">
        <div class="alert" :class="isAuthenticated ? 'alert-success' : 'alert-warning'">
          <strong>Status:</strong> {{ isAuthenticated ? 'Authenticated' : 'Not Authenticated' }}
        </div>
        
        <div v-if="isAuthenticated">
          <button class="btn btn-outline-danger me-2" @click="logout">Logout</button>
        </div>
        <div v-else>
          <button class="btn btn-primary me-2" @click="googleLogin">Google Login</button>
          <button class="btn btn-outline-secondary" @click="getDevToken">Get Dev Token</button>
        </div>
      </div>
    </div>
    
    <div class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h2>API Endpoints Test</h2>
        <div class="form-check form-switch">
          <input class="form-check-input" type="checkbox" v-model="includeAuth" id="includeAuthSwitch">
          <label class="form-check-label" for="includeAuthSwitch">Include Auth Token</label>
        </div>
      </div>
      <div class="card-body">
        <div class="endpoint-list">
          <div v-for="(endpoint, index) in endpoints" :key="index" class="endpoint-item mb-3 p-3 border rounded">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <div>
                <span class="badge" :class="getBadgeClass(endpoint.method)">{{ endpoint.method }}</span>
                <strong class="ms-2">{{ endpoint.url }}</strong>
              </div>
              <button class="btn btn-sm btn-primary" @click="testEndpoint(endpoint)">Test</button>
            </div>
            <div v-if="endpoint.description" class="mb-2 text-muted">{{ endpoint.description }}</div>
            <div v-if="endpoint.response" class="mt-3">
              <div class="d-flex align-items-center mb-2">
                <span class="badge" :class="getResponseBadgeClass(endpoint.status)">Status: {{ endpoint.status }}</span>
                <span class="ms-2">Response time: {{ endpoint.responseTime }}ms</span>
              </div>
              <pre class="response-box p-3 bg-light">{{ JSON.stringify(endpoint.response, null, 2) }}</pre>
            </div>
            <div v-if="endpoint.error" class="mt-3">
              <div class="alert alert-danger">
                <strong>Error:</strong> {{ endpoint.error }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card mb-4">
      <div class="card-header">
        <h2>Custom API Request</h2>
      </div>
      <div class="card-body">
        <div class="mb-3 row">
          <div class="col-md-2">
            <select class="form-select" v-model="customRequest.method">
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="DELETE">DELETE</option>
            </select>
          </div>
          <div class="col-md-10">
            <input type="text" class="form-control" v-model="customRequest.url" placeholder="API endpoint (e.g., /api/pets)" />
          </div>
        </div>
        
        <div class="mb-3" v-if="customRequest.method !== 'GET'">
          <label class="form-label">Request Body (JSON)</label>
          <textarea class="form-control" v-model="customRequest.body" rows="5" placeholder='{"key": "value"}'></textarea>
        </div>
        
        <button class="btn btn-primary" @click="testCustomEndpoint">Send Request</button>
        
        <div v-if="customRequest.response" class="mt-4">
          <div class="d-flex align-items-center mb-2">
            <span class="badge" :class="getResponseBadgeClass(customRequest.status)">Status: {{ customRequest.status }}</span>
            <span class="ms-2">Response time: {{ customRequest.responseTime }}ms</span>
          </div>
          <pre class="response-box p-3 bg-light">{{ JSON.stringify(customRequest.response, null, 2) }}</pre>
        </div>
        
        <div v-if="customRequest.error" class="mt-4">
          <div class="alert alert-danger">
            <strong>Error:</strong> {{ customRequest.error }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="card mb-4">
      <div class="card-header">
        <h2>Debug Information</h2>
      </div>
      <div class="card-body">
        <h5>Local Storage:</h5>
        <pre class="debug-box p-3 bg-light">{{ debugLocalStorage }}</pre>
        
        <h5 class="mt-3">Browser Information:</h5>
        <pre class="debug-box p-3 bg-light">{{ browserInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ApiTestComponent',
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || window.location.origin,
      envApiBaseUrl: import.meta.env.VITE_API_BASE_URL,
      editingBaseUrl: false,
      isAuthenticated: !!localStorage.getItem('access_token'),
      includeAuth: true,
      endpoints: [
        {
          method: 'GET', 
          url: '/api/auth/login_info',
          description: 'Get authentication configuration',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/auth/google',
          description: 'Test Google auth redirect (will navigate away)',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/auth/check',
          description: 'Check authentication status',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/auth/user',
          description: 'Get current user information',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/pets',
          description: 'Get all pets for current user',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/devices',
          description: 'Get all devices for current user',
          response: null,
          status: null,
          responseTime: null,
          error: null
        },
        {
          method: 'GET',
          url: '/api/locations/recent?limit=5',
          description: 'Get 5 recent locations',
          response: null,
          status: null,
          responseTime: null,
          error: null
        }
      ],
      customRequest: {
        method: 'GET',
        url: '',
        body: '',
        response: null,
        status: null,
        responseTime: null,
        error: null
      }
    };
  },
  computed: {
    debugLocalStorage() {
      const storage = {};
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        let value = localStorage.getItem(key);
        
        // Try to parse JSON
        try {
          value = JSON.parse(value);
        } catch (e) {
          // Not JSON, leave as is
        }
        
        storage[key] = value;
      }
      return JSON.stringify(storage, null, 2);
    },
    browserInfo() {
      return {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        cookiesEnabled: navigator.cookieEnabled,
        location: window.location.href,
        protocol: window.location.protocol,
        host: window.location.host
      };
    }
  },
  methods: {
    getBadgeClass(method) {
      const classes = {
        GET: 'bg-success',
        POST: 'bg-primary',
        PUT: 'bg-warning',
        DELETE: 'bg-danger'
      };
      return classes[method] || 'bg-secondary';
    },
    getResponseBadgeClass(status) {
      if (!status) return 'bg-secondary';
      if (status >= 200 && status < 300) return 'bg-success';
      if (status >= 300 && status < 400) return 'bg-info';
      if (status >= 400 && status < 500) return 'bg-warning';
      return 'bg-danger';
    },
    getAuthHeader() {
      const token = localStorage.getItem('access_token');
      return token && this.includeAuth ? { Authorization: `Bearer ${token}` } : {};
    },
    async testEndpoint(endpoint) {
      endpoint.response = null;
      endpoint.error = null;
      endpoint.status = null;
      endpoint.responseTime = null;
      
      // Special handling for Google Auth endpoint which causes redirect
      if (endpoint.url === '/api/auth/google') {
        if (confirm('Testing Google Auth will redirect you away from this page. Continue?')) {
          window.location.href = `${this.apiBaseUrl}${endpoint.url}`;
        } else {
          endpoint.response = { message: 'Redirect cancelled by user' };
          endpoint.status = 0;
        }
        return;
      }
      
      const startTime = performance.now();
      
      try {
        const baseUrl = this.apiBaseUrl;
        const url = `${baseUrl}${endpoint.url}`;
        console.log(`Testing endpoint: ${endpoint.method} ${url}`);
        
        const headers = this.getAuthHeader();
        console.log('Headers:', headers);
        
        const config = { headers };
        let response;
        
        switch (endpoint.method) {
          case 'GET':
            response = await axios.get(url, config);
            break;
          case 'POST':
            response = await axios.post(url, {}, config);
            break;
          case 'PUT':
            response = await axios.put(url, {}, config);
            break;
          case 'DELETE':
            response = await axios.delete(url, config);
            break;
        }
        
        endpoint.response = response.data;
        endpoint.status = response.status;
      } catch (error) {
        console.error('API test error:', error);
        endpoint.error = error.message;
        if (error.response) {
          endpoint.status = error.response.status;
          endpoint.response = error.response.data;
        }
      } finally {
        endpoint.responseTime = Math.round(performance.now() - startTime);
      }
    },
    async testCustomEndpoint() {
      this.customRequest.response = null;
      this.customRequest.error = null;
      this.customRequest.status = null;
      this.customRequest.responseTime = null;
      
      const startTime = performance.now();
      
      try {
        const baseUrl = this.apiBaseUrl;
        const url = `${baseUrl}${this.customRequest.url}`;
        console.log(`Testing custom endpoint: ${this.customRequest.method} ${url}`);
        
        const headers = this.getAuthHeader();
        console.log('Headers:', headers);
        
        const config = { headers };
        let response;
        let body = {};
        
        if (this.customRequest.method !== 'GET' && this.customRequest.body) {
          try {
            body = JSON.parse(this.customRequest.body);
          } catch (e) {
            this.customRequest.error = 'Invalid JSON in request body';
            return;
          }
        }
        
        switch (this.customRequest.method) {
          case 'GET':
            response = await axios.get(url, config);
            break;
          case 'POST':
            response = await axios.post(url, body, config);
            break;
          case 'PUT':
            response = await axios.put(url, body, config);
            break;
          case 'DELETE':
            response = await axios.delete(url, config);
            break;
        }
        
        this.customRequest.response = response.data;
        this.customRequest.status = response.status;
      } catch (error) {
        console.error('Custom API test error:', error);
        this.customRequest.error = error.message;
        if (error.response) {
          this.customRequest.status = error.response.status;
          this.customRequest.response = error.response.data;
        }
      } finally {
        this.customRequest.responseTime = Math.round(performance.now() - startTime);
      }
    },
    googleLogin() {
      window.location.href = '/api/auth/google';
    },
    getDevToken() {
      window.location.href = '/api/auth/dev-token';
    },
    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      this.isAuthenticated = false;
    },
    toggleEditBaseUrl() {
      if (this.editingBaseUrl) {
        // Save mode - just toggle off edit mode
        this.editingBaseUrl = false;
        console.log(`API Base URL changed to: ${this.apiBaseUrl}`);
      } else {
        // Edit mode - enable editing
        this.editingBaseUrl = true;
      }
    },
    setApiBaseUrl(url) {
      this.apiBaseUrl = url;
      console.log(`API Base URL set to: ${url}`);
    }
  }
};
</script>

<style scoped>
.api-test-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  margin-bottom: 25px;
  font-size: 28px;
  color: var(--primary);
}

.endpoint-item {
  background-color: white;
  transition: all 0.2s ease;
}

.endpoint-item:hover {
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
}

.response-box, 
.debug-box {
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

pre {
  margin-bottom: 0;
}
</style>