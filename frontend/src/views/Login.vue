<template>
  <div class="container py-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card shadow">
          <div class="card-body p-4">
            <h2 class="text-center mb-4">Log In to PetTracker</h2>
            
            <div v-if="loading" class="text-center my-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Redirecting to Google login...</p>
            </div>
            
            <div v-else>
              <p class="text-center text-muted mb-4">
                Sign in with your Google account for secure access to your pet tracking dashboard.
              </p>
              
              <div v-if="true" class="d-grid gap-2">
                <button class="btn btn-primary btn-lg" @click="loginWithGoogle">
                  <i class="bi bi-google me-2"></i> Log in with Google
                </button>
              </div>
              
              <div v-if="error" class="alert alert-danger mt-3" role="alert">
                {{ error }}
              </div>
              
              <div class="text-center mt-4">
                <p class="text-muted">
                  <small>Need help? <a href="#">Contact Support</a></small>
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="isDevEnvironment" class="card mt-4 shadow-sm">
          <div class="card-body">
            <h5 class="card-title">Developer Options</h5>
            <p class="card-text">
              These options are only available in development mode.
            </p>
            <div class="d-grid gap-2">
              <router-link to="/dev-token" class="btn btn-secondary">
                Get Development Token
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../services/api';
import apiClient from '../services/api';

export default {
  data() {
    return {
      isDevEnvironment: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
      loading: false,
      error: null,
      googleConfigured: true,
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
    };
  },
  async created() {
    // Check for error parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const errorMsg = urlParams.get('error');
    if (errorMsg) {
      this.error = decodeURIComponent(errorMsg);
    }
    
    // Check if Google OAuth is configured by calling login_info
    try {
      console.log('Making API request to get login info');
      const response = await authAPI.getLoginInfo();
      this.googleConfigured = response.data.googleConfigured;
      
      if (!this.googleConfigured) {
        this.error = 'Google authentication is not configured. Please contact the administrator.';
      } else {
        console.log('Google OAuth is properly configured');
      }
    } catch (err) {
      console.error('Failed to check Google OAuth configuration:', err);
      // Just assume it's configured if we can't check
      this.googleConfigured = true;
    }
  },
  methods: {
    async loginWithGoogle() {
      if (!this.googleConfigured) {
        this.error = 'Google authentication is not configured. Please contact the administrator.';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      // Log information for debugging
      console.log(`Using API base URL for login: ${this.apiBaseUrl}`);
      
      // Directly redirect to Google login using our configured API base URL
      window.location.href = `${this.apiBaseUrl}/api/auth/login`;
    }
  }
};
</script>
