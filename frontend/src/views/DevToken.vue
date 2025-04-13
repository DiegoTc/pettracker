<template>
  <div class="container my-4">
    <div class="card">
      <div class="card-header">
        <h2>Developer Token</h2>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status"></div>
          <p>Loading...</p>
        </div>
        
        <div v-else-if="error" class="alert alert-danger">
          <h4>Error</h4>
          <p>{{ error }}</p>
          <button class="btn btn-primary mt-2" @click="getToken">Try Again</button>
        </div>
        
        <div v-else-if="token">
          <div class="alert alert-success">
            <p><strong>Development token generated successfully!</strong></p>
            <p>User ID: {{ userId }}</p>
          </div>
          
          <div class="mb-3">
            <label class="form-label">Access Token:</label>
            <div class="input-group">
              <input type="text" class="form-control" :value="token" readonly ref="tokenInput" />
              <button class="btn btn-outline-primary" @click="copyToken">
                <i class="bi bi-clipboard me-1"></i> Copy
              </button>
            </div>
            <div v-if="copied" class="text-success mt-1">
              <small><i class="bi bi-check-circle-fill"></i> Token copied to clipboard!</small>
            </div>
          </div>
          
          <div class="mt-4">
            <button class="btn btn-primary me-2" @click="saveAndRedirect">
              Save Token & Go to Dashboard
            </button>
            <button class="btn btn-outline-secondary" @click="getToken">
              Generate New Token
            </button>
          </div>
          
          <div class="alert alert-warning mt-4">
            <h5>Developer Use Only</h5>
            <p>This token is for development and testing purposes only. It should not be used in production.</p>
          </div>
        </div>
        
        <div v-else>
          <p>Click the button below to generate a development token for testing the API:</p>
          <button class="btn btn-primary" @click="getToken">
            Generate Dev Token
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DevToken',
  data() {
    return {
      token: null,
      userId: null,
      loading: false,
      error: null,
      copied: false
    };
  },
  methods: {
    async getToken() {
      this.loading = true;
      this.token = null;
      this.error = null;
      this.copied = false;
      
      try {
        const response = await fetch('/api/auth/dev-token/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Server responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        this.token = data.access_token;
        this.userId = data.user_id;
      } catch (error) {
        console.error('Error getting dev token:', error);
        this.error = `Failed to get development token: ${error.message}`;
      } finally {
        this.loading = false;
      }
    },
    
    copyToken() {
      const tokenInput = this.$refs.tokenInput;
      tokenInput.select();
      document.execCommand('copy');
      this.copied = true;
      
      // Reset the "copied" message after 3 seconds
      setTimeout(() => {
        this.copied = false;
      }, 3000);
    },
    
    saveAndRedirect() {
      if (this.token) {
        localStorage.setItem('access_token', this.token);
        console.log('Development token saved to localStorage');
        this.$router.push('/');
      }
    }
  }
};
</script>
