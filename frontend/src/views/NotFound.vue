<template>
  <div class="not-found-page text-center py-5">
    <div class="mb-4">
      <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
    </div>
    <h1 class="mb-3">Page Not Found</h1>
    <p class="lead mb-4">Sorry, we couldn't find the page you're looking for.</p>
    <div class="d-flex justify-content-center">
      <router-link to="/" class="btn btn-primary me-3">
        <i class="bi bi-house-door me-1"></i> Go Home
      </router-link>
      <button class="btn btn-outline-secondary" @click="goBack">
        <i class="bi bi-arrow-left me-1"></i> Go Back
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound',
  methods: {
    goBack() {
      this.$router.go(-1);
    }
  }
};
</script>

<style scoped>
.not-found-page {
  margin: 3rem auto;
  max-width: 600px;
}
</style>
