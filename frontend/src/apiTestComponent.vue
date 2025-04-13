<template>
  <div class="container mt-4">
    <div class="card">
      <div class="card-header">
        <h3>API Test Component</h3>
      </div>
      <div class="card-body">
        <div class="mb-4">
          <h4>API Configuration</h4>
          <div class="alert alert-info">
            <strong>Base URL:</strong> {{ apiBaseUrl || 'None (using relative URLs)' }}
          </div>
        </div>

        <div class="mb-4">
          <h4>API Test</h4>
          <button class="btn btn-primary me-2" @click="testAuth">
            Test Authentication
          </button>
          <button class="btn btn-secondary me-2" @click="testGetPets">
            Test Get Pets
          </button>
          <button class="btn btn-info" @click="testDirectFetch">
            Test Direct API Call
          </button>
        </div>

        <div v-if="loading" class="d-flex justify-content-center mb-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-if="result" class="mt-4">
          <h4>Result:</h4>
          <div :class="{'alert alert-success': !error, 'alert alert-danger': error}">
            <pre>{{ JSON.stringify(result, null, 2) }}</pre>
          </div>
        </div>
        
        <div class="mt-4">
          <h4>Console Output</h4>
          <p class="text-muted">Check the browser console (F12) for detailed logs</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { authAPI, petsAPI } from './services/api';

export default {
  data() {
    return {
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || null,
      loading: false,
      result: null,
      error: false
    };
  },
  mounted() {
    console.log('API Test Component mounted');
    console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
  },
  methods: {
    async testAuth() {
      try {
        this.loading = true;
        this.result = null;
        this.error = false;
        
        console.log('Testing authentication endpoint...');
        const response = await authAPI.checkAuth();
        
        this.result = {
          status: response.status,
          data: response.data,
          headers: response.headers,
          timestamp: new Date().toISOString()
        };
      } catch (err) {
        this.error = true;
        this.result = {
          error: err.message,
          response: err.response?.data,
          status: err.response?.status,
          timestamp: new Date().toISOString()
        };
      } finally {
        this.loading = false;
      }
    },
    
    async testGetPets() {
      try {
        this.loading = true;
        this.result = null;
        this.error = false;
        
        console.log('Testing pets endpoint...');
        const response = await petsAPI.getAll();
        
        this.result = {
          status: response.status,
          data: response.data,
          timestamp: new Date().toISOString()
        };
      } catch (err) {
        this.error = true;
        this.result = {
          error: err.message,
          response: err.response?.data,
          status: err.response?.status,
          timestamp: new Date().toISOString()
        };
      } finally {
        this.loading = false;
      }
    },
    
    async testDirectFetch() {
      try {
        this.loading = true;
        this.result = null;
        this.error = false;
        
        // This will use a direct axios call to the full URL
        const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';
        console.log(`Making direct API call to ${apiUrl}/api/auth/check`);
        
        const response = await axios.get(`${apiUrl}/api/auth/check`, {
          withCredentials: true
        });
        
        this.result = {
          method: 'Direct API call',
          url: `${apiUrl}/api/auth/check`,
          status: response.status,
          data: response.data,
          timestamp: new Date().toISOString()
        };
      } catch (err) {
        this.error = true;
        this.result = {
          error: err.message,
          response: err.response?.data,
          status: err.response?.status,
          timestamp: new Date().toISOString()
        };
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>