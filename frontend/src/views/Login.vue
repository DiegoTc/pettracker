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
              
              <div v-if="loginInfo.googleConfigured" class="d-grid gap-2">
                <button class="btn btn-primary btn-lg" @click="loginWithGoogle">
                  <i class="bi bi-google me-2"></i> Log in with Google
                </button>
              </div>
              
              <div v-else class="alert alert-warning" role="alert">
                <strong>Google OAuth not configured!</strong>
                <p class="mb-0">The Google login feature is not properly configured. Please contact the administrator.</p>
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
import { authAPI } from '@/services/api';

export default {
  data() {
    return {
      loginInfo: {
        googleConfigured: false
      },
      isDevEnvironment: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1',
      loading: false,
      error: null
    };
  },
  methods: {
    async loginWithGoogle() {
      this.loading = true;
      this.error = null;
      
      try {
        // Use the authAPI client which has the correct API URL configuration
        const response = await authAPI.login();
        
        if (response.data && response.data.redirect_url) {
          // Redirect to Google OAuth
          window.location.href = response.data.redirect_url;
        } else {
          console.error('Invalid login response:', response.data);
          this.error = 'Unable to initiate login. Please ensure Google OAuth is configured.';
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = 'Failed to initiate login. Please check the server connection.';
        this.loading = false;
      }
    },
    async checkLoginInfo() {
      try {
        const response = await authAPI.getLoginInfo();
        this.loginInfo = response.data;
      } catch (error) {
        console.error('Failed to get login info:', error);
        this.error = 'Failed to check authentication configuration.';
      }
    }
  },
  created() {
    // Check for error parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const errorMsg = urlParams.get('error');
    if (errorMsg) {
      this.error = decodeURIComponent(errorMsg);
    }
    
    // Check login configuration
    this.checkLoginInfo();
  }
};
</script>
