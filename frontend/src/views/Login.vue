<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- Logo and App Name -->
      <div class="login-header">
        <div class="app-logo">
          <i class="bi bi-heart-fill"></i>
        </div>
        <h1 class="app-name">PetTracker</h1>
        <p class="app-description">Your pet's safety, simplified.</p>
      </div>
      
      <!-- Login Card -->
      <div class="login-card">
        <h2 class="login-title">Sign In</h2>
        
        <div v-if="loading" class="loading-container">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="loading-text">Redirecting to Google login...</p>
        </div>
        
        <div v-else class="login-content">
          <p class="login-description">
            Sign in with your Google account for secure access to your pet tracking dashboard.
          </p>
          
          <div class="login-button-container">
            <button class="login-button google-button" @click="loginWithGoogle">
              <i class="bi bi-google"></i> Continue with Google
            </button>
          </div>
          
          <div v-if="error" class="login-error">
            <i class="bi bi-exclamation-triangle"></i>
            <span>{{ error }}</span>
          </div>
          
          <div class="help-link">
            <p>Need help? <a href="#">Contact Support</a></p>
          </div>
        </div>
      </div>
      
      <!-- Developer Options -->
      <div v-if="isDevEnvironment" class="dev-options">
        <h3>Developer Options</h3>
        <p>These options are only available in development mode.</p>
        <router-link to="/dev-token" class="dev-button">
          Get Development Token
        </router-link>
      </div>
      
      <!-- Footer -->
      <div class="login-footer">
        <p>&copy; {{ new Date().getFullYear() }} PetTracker. All rights reserved.</p>
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

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fb;
  padding: 20px;
}

.login-wrapper {
  width: 100%;
  max-width: 480px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.app-logo {
  width: 80px;
  height: 80px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
  font-size: 36px;
  box-shadow: 0 10px 20px rgba(33, 150, 243, 0.2);
}

.app-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.app-description {
  font-size: 16px;
  color: var(--text-light);
  max-width: 260px;
  margin: 0 auto;
}

.login-card {
  width: 100%;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  padding: 32px;
  margin-bottom: 20px;
  text-align: center;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--text);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.loading-text {
  margin-top: 16px;
  color: var(--text-light);
}

.login-description {
  color: var(--text-light);
  font-size: 15px;
  margin-bottom: 24px;
  line-height: 1.5;
}

.login-button-container {
  margin-bottom: 24px;
}

.login-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 48px;
  border-radius: 24px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 15px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.google-button {
  background-color: var(--background);
  color: var(--text);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}

.google-button:hover {
  background-color: #f8f9fa;
  box-shadow: var(--shadow-md);
}

.google-button i {
  margin-right: 10px;
  font-size: 18px;
  color: #4285F4;
}

.login-error {
  display: flex;
  align-items: center;
  background-color: rgba(244, 67, 54, 0.1);
  color: var(--danger);
  padding: 12px 16px;
  border-radius: var(--radius);
  margin-bottom: 20px;
  font-size: 14px;
  text-align: left;
}

.login-error i {
  margin-right: 10px;
  font-size: 16px;
  flex-shrink: 0;
}

.help-link {
  font-size: 14px;
  color: var(--text-light);
}

.help-link a {
  color: var(--primary);
  text-decoration: none;
  transition: color 0.3s ease;
}

.help-link a:hover {
  color: var(--primary-dark);
  text-decoration: underline;
}

.dev-options {
  width: 100%;
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  padding: 20px;
  margin-bottom: 20px;
  border-left: 4px solid var(--secondary);
}

.dev-options h3 {
  font-size: 18px;
  margin-bottom: 10px;
  color: var(--text);
}

.dev-options p {
  font-size: 14px;
  color: var(--text-light);
  margin-bottom: 15px;
}

.dev-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 42px;
  padding: 0 20px;
  border-radius: 21px;
  background-color: var(--secondary);
  color: white;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.3s ease;
}

.dev-button:hover {
  background-color: #e91e63;
  box-shadow: 0 4px 10px rgba(255, 64, 129, 0.3);
}

.login-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: var(--text-light);
}

/* Responsive adjustments */
@media (max-width: 576px) {
  .login-card,
  .dev-options {
    padding: 24px 20px;
  }
  
  .app-name {
    font-size: 24px;
  }
  
  .app-logo {
    width: 70px;
    height: 70px;
    font-size: 32px;
  }
}
</style>
