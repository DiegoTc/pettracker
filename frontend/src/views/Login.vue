<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-logo">
        <i class="bi bi-shield-check"></i>
        <h1>PetTracker</h1>
      </div>
      
      <div class="login-subtitle">
        <h2>Welcome Back</h2>
        <p>Sign in to continue to your account</p>
      </div>
      
      <div class="login-options">
        <button class="btn btn-google" @click="googleLogin">
          <i class="bi bi-google"></i>
          Sign in with Google
        </button>
      </div>
      
      <div class="login-footer">
        <p>&copy; {{ new Date().getFullYear() }} PetTracker. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  methods: {
    googleLogin() {
      window.location.href = '/api/auth/google';
    }
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--background);
  padding: 20px;
}

.login-card {
  background-color: var(--card-bg);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  width: 100%;
  max-width: 420px;
  padding: 40px;
  text-align: center;
}

.login-logo {
  margin-bottom: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.login-logo i {
  font-size: 60px;
  color: var(--primary);
  margin-bottom: 16px;
}

.login-logo h1 {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 28px;
  color: var(--text);
}

.login-subtitle {
  margin-bottom: 32px;
}

.login-subtitle h2 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text);
}

.login-subtitle p {
  color: var(--text-light);
  font-size: 16px;
}

.login-options {
  margin-bottom: 32px;
}

.btn-google {
  width: 100%;
  padding: 12px 24px;
  background-color: #4285F4;
  color: white;
  font-size: 16px;
  font-weight: 500;
  transition: background-color 0.2s ease, transform 0.2s ease;
}

.btn-google:hover {
  background-color: #3367D6;
  transform: translateY(-2px);
}

.btn-google i {
  margin-right: 8px;
  font-size: 18px;
}

.login-footer {
  font-size: 14px;
  color: var(--text-lighter);
}
</style>