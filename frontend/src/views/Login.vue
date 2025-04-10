<template>
  <div class="login-page">
    <div class="row justify-content-center">
      <div class="col-md-6 col-lg-5">
        <div class="card">
          <div class="card-header text-center py-4">
            <h2 class="mb-0">Pet Tracker</h2>
          </div>
          <div class="card-body p-4">
            <div class="text-center mb-4">
              <h3>Sign In</h3>
              <p class="text-muted">Use your Google account to sign in</p>
            </div>
            
            <div v-if="error" class="alert alert-danger">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              {{ error }}
            </div>
            
            <div class="text-center">
              <button 
                class="btn btn-primary btn-lg w-100" 
                @click="loginWithGoogle"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                <i v-else class="bi bi-google me-2"></i>
                Sign in with Google
              </button>
            </div>
            
            <div class="text-center mt-4">
              <p class="text-muted">
                By signing in, you agree to our Terms of Service and Privacy Policy.
              </p>
            </div>
          </div>
        </div>
        
        <div class="card mt-4">
          <div class="card-body">
            <h5>About Pet Tracker</h5>
            <p>
              Pet Tracker is a comprehensive platform that enables you to monitor, interact with, 
              and care for your pets using advanced tracking technology. Keep track of your pets' 
              location, activity, and health status in real-time.
            </p>
            <div class="features mt-3">
              <div class="feature">
                <i class="bi bi-geo-alt-fill text-primary me-2"></i>
                <span>Real-time GPS tracking</span>
              </div>
              <div class="feature">
                <i class="bi bi-activity text-primary me-2"></i>
                <span>Activity monitoring</span>
              </div>
              <div class="feature">
                <i class="bi bi-heart-fill text-primary me-2"></i>
                <span>Health status updates</span>
              </div>
              <div class="feature">
                <i class="bi bi-clock-history text-primary me-2"></i>
                <span>Location history</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { authAPI } from '../services/api';

export default {
  name: 'Login',
  data() {
    return {
      loading: false,
      error: null
    };
  },
  methods: {
    async loginWithGoogle() {
      this.loading = true;
      this.error = null;
      
      try {
        // Make a direct request to the backend instead of using the API client
        // This bypasses any proxy issues
        const response = await fetch('/api/auth/login/', {
          method: 'GET',
          credentials: 'include',
          headers: {
            'Accept': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data && data.redirect_url) {
          // Redirect to Google OAuth
          window.location.href = data.redirect_url;
        } else {
          console.error('Invalid login response:', data);
          this.error = 'Unable to initiate login. Please ensure Google OAuth is configured.';
        }
      } catch (error) {
        console.error('Login error:', error);
        this.error = 'Failed to initiate login. Please check the server connection.';
        this.loading = false;
      }
    },
  },
  created() {
    // Check for error message in URL parameters (e.g., after failed OAuth)
    const urlParams = new URLSearchParams(window.location.search);
    const errorMsg = urlParams.get('error');
    if (errorMsg) {
      this.error = decodeURIComponent(errorMsg);
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  padding: 40px 0;
  background-color: var(--bs-gray-100);
  display: flex;
  align-items: center;
}

.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  border-bottom: none;
  border-top-left-radius: 12px !important;
  border-top-right-radius: 12px !important;
}

.btn-primary {
  padding: 12px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(var(--bs-primary-rgb), 0.2);
}

.features {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.feature {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .login-page {
    padding: 20px 0;
  }
}
</style>
