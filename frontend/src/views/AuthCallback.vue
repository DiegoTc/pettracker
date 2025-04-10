<template>
  <div class="text-center p-5">
    <h3>Processing login...</h3>
    <div class="spinner-border" role="status"></div>
    <p v-if="error" class="text-danger mt-3">{{ error }}</p>
  </div>
</template>

<script>
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
      // If no token but we have a code, we need to redirect to the backend
      const code = urlParams.get('code');
      const error = urlParams.get('error');
      
      if (error) {
        console.error('Authentication error:', error);
        this.error = `Authentication error: ${error}`;
        setTimeout(() => {
          this.$router.push(`/login?error=${encodeURIComponent(error)}`);
        }, 2000);
      } else if (code) {
        console.log('Received OAuth code, redirecting to backend for processing');
        
        // Create absolute URL to ensure we're hitting the backend directly
        const apiBaseUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
          ? 'http://localhost:5000' 
          : window.location.origin;
          
        // Get all existing parameters from the URL
        const existingParams = Array.from(urlParams.entries())
          .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
          .join('&');
          
        // Redirect to backend with all the original Google parameters
        window.location.href = `${apiBaseUrl}/api/auth/callback?${existingParams}`;
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
