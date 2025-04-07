<template>
  <div class="not-found text-center py-5">
    <i class="bi bi-exclamation-circle display-1 text-muted"></i>
    <h1 class="mt-4">Page Not Found</h1>
    <p class="lead">The page you are looking for does not exist.</p>
    <router-link to="/" class="btn btn-primary mt-3">
      Return to Home
    </router-link>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
};
</script>

<style scoped>
.not-found {
  margin: 50px 0;
}
</style>
