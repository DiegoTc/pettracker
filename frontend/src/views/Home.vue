<template>
  <div class="home">
    <div class="jumbotron bg-light p-5 rounded">
      <h1 class="display-4">Welcome to Pet Tracker</h1>
      <p class="lead">A comprehensive solution for tracking and managing your pets</p>
      <hr class="my-4">
      <p>Track your pets in real-time, monitor their health, and keep them safe.</p>
      <div v-if="!isAuthenticated">
        <a href="/api/auth/login" class="btn btn-primary btn-lg">
          <i class="bi bi-google me-2"></i> Sign in with Google
        </a>
      </div>
      <div v-else>
        <router-link to="/pets" class="btn btn-primary btn-lg">
          View My Pets
        </router-link>
      </div>
    </div>

    <div class="row mt-5">
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <h3 class="card-title">Real-time Tracking</h3>
            <p class="card-text">Monitor your pet's location in real-time using our advanced tracking devices.</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <h3 class="card-title">Health Monitoring</h3>
            <p class="card-text">Keep track of your pet's health metrics and get notified of any changes.</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body text-center">
            <h3 class="card-title">Safe Zones</h3>
            <p class="card-text">Define safe areas for your pets and receive alerts if they leave these zones.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Home',
  data() {
    return {
      isAuthenticated: false
    };
  },
  async created() {
    try {
      const response = await axios.get('/api/auth/check');
      this.isAuthenticated = response.data.authenticated;
    } catch (error) {
      console.error('Error checking authentication:', error);
      this.isAuthenticated = false;
    }
  }
};
</script>

<style scoped>
.home {
  margin-bottom: 50px;
}
</style>
