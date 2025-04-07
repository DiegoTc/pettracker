<template>
  <div class="login-page">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-primary text-white text-center">
            <h4>Sign In</h4>
          </div>
          <div class="card-body">
            <div class="text-center mb-4">
              <p>Sign in with your Google account to access Pet Tracker</p>
              <a href="/api/auth/login" class="btn btn-primary btn-lg">
                <i class="bi bi-google me-2"></i> Sign in with Google
              </a>
            </div>
            
            <hr>
            
            <div class="text-center mt-4">
              <p class="text-muted">Pet Tracker securely manages your data and only uses your 
              Google account for authentication purposes. We don't store your Google password.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login'
};
</script>

<style scoped>
.login-page {
  margin-top: 40px;
}
</style>
