<template>
  <div class="text-center p-5">
    <h3>Processing login...</h3>
    <div class="spinner-border" role="status"></div>
    <p v-if="error" class="text-danger mt-3">{{ error }}</p>
  </div>
</template>

<script>
import apiClient from '../services/api';

export default {
  data() {
    return {
      error: null
    };
  },
  created() {
    // First check for token in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    
    if (token) {
      // Store token in localStorage
      localStorage.setItem('access_token', token);
      console.log('Authentication token stored from callback');
      
      // Redirect to home or saved redirect URL
      const redirect = localStorage.getItem('login_redirect') || '/';
      localStorage.removeItem('login_redirect');
      this.$router.push(redirect);
    } else {
      // No token, check for code to send to backend
      const code = urlParams.get('code');
      
      if (code) {
        // Call backend to complete OAuth flow
        apiClient.get(`/api/auth/callback?code=${code}`)
          .then(response => {
            if (response.data && response.data.access_token) {
              // Store the token in localStorage
              localStorage.setItem('access_token', response.data.access_token);
              console.log('Authentication successful, token stored');
              
              // Redirect to home or saved redirect URL
              const redirect = localStorage.getItem('login_redirect') || '/';
              localStorage.removeItem('login_redirect');
              this.$router.push(redirect);
            } else {
              console.error('No access token in response');
              this.error = 'Authentication failed: No access token received';
            }
          })
          .catch(error => {
            console.error('Error processing callback:', error);
            this.error = `Authentication failed: ${error.message}`;
          });
      } else {
        // No code or token parameter
        this.error = 'No authentication code or token received';
        setTimeout(() => {
          this.$router.push('/login?error=No authentication data received');
        }, 3000);
      }
    }
  }
};
</script>
