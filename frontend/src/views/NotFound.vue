<template>
  <div class="not-found">
    <div class="error-icon">
      <i class="bi bi-exclamation-triangle"></i>
    </div>
    <h1>404</h1>
    <h2>Page Not Found</h2>
    <p>The page you are looking for does not exist or has been moved.</p>
    <router-link to="/" class="btn btn-primary">
      <i class="bi bi-house-door"></i> Go to Home
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  background-color: var(--background);
}

.error-icon {
  font-size: 80px;
  color: var(--warning);
  margin-bottom: 20px;
}

h1 {
  font-size: 80px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text);
}

h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text);
}

p {
  font-size: 18px;
  color: var(--text-light);
  max-width: 500px;
  margin-bottom: 30px;
}

.btn {
  font-size: 16px;
  padding: 12px 24px;
}
</style>