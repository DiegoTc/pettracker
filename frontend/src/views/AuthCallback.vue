<template>
  <div class="text-center p-5">
    <h3>{{ message }}</h3>
    <div v-if="loading" class="spinner-border" role="status"></div>
    <p v-if="error" class="text-danger mt-3">{{ error }}</p>
  </div>
</template>

<script>
import apiClient from '../services/api';  

export default {
  data() {
    return {
      loading: true,
      error: null,
      message: 'Processing login...',
      apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'
    };
  },
  created() {
    // First check for token in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // Store token in localStorage
      localStorage.setItem('access_token', token);
      
      // Set authentication indicator in localStorage
      localStorage.setItem('is_authenticated', 'true');
      
      console.log('Authentication token stored from callback');
      this.message = 'Authentication successful! Redirecting...';
      
      // Redirect to home or saved redirect URL
      const redirect = localStorage.getItem('login_redirect') || '/';
      localStorage.removeItem('login_redirect');
      
      // Short delay to ensure smooth UI transition
      setTimeout(() => {
        this.$router.push(redirect);
      }, 1000);
    } else {
      // If no token but we have a code, we need to redirect to the backend
      const code = urlParams.get('code');
      const error = urlParams.get('error');
      
      if (error) {
        console.error('Authentication error:', error);
        this.error = `Authentication error: ${error}`;
        this.loading = false;
        this.message = 'Authentication failed';
        
        setTimeout(() => {
          this.$router.push(`/login?error=${encodeURIComponent(error)}`);
        }, 2000);
      } else if (code) {
        console.log('Received OAuth code, redirecting to backend for processing');
        this.message = 'Processing OAuth callback...';
        
        // Log the API base URL for debugging purposes
        console.log(`Using API base URL for callback: ${this.apiBaseUrl}`);
          
        // Get all existing parameters from the URL
        const existingParams = Array.from(urlParams.entries())
          .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
          .join('&');
          
        // Redirect to backend with all the original Google parameters
        // Using the consistent apiBaseUrl from the data property
        window.location.href = `${this.apiBaseUrl}/api/auth/callback?${existingParams}`;
      } else {
        // No code or token parameter
        this.error = 'No authentication code or token received';
        this.loading = false;
        this.message = 'Authentication incomplete';
        
        setTimeout(() => {
          this.$router.push('/login?error=No authentication data received');
        }, 3000);
      }
    }
  }
};
</script>
