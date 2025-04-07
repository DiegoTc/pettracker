<template>
  <div class="app-container">
    <header>
      <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
          <router-link class="navbar-brand" to="/">Pet Tracker</router-link>
          <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
              <li class="nav-item">
                <router-link class="nav-link" to="/">Home</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated">
                <router-link class="nav-link" to="/pets">My Pets</router-link>
              </li>
              <li class="nav-item" v-if="isAuthenticated">
                <router-link class="nav-link" to="/devices">My Devices</router-link>
              </li>
            </ul>
            <div class="d-flex" v-if="isAuthenticated">
              <span class="navbar-text me-3">
                Welcome, {{ user.username }}
              </span>
              <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
            </div>
            <div v-else>
              <router-link to="/login" class="btn btn-outline-light btn-sm">Login</router-link>
            </div>
          </div>
        </div>
      </nav>
    </header>

    <main class="container my-4">
      <router-view />
    </main>

    <footer class="bg-dark text-light py-3 mt-5">
      <div class="container text-center">
        <p class="mb-0">&copy; {{ new Date().getFullYear() }} Pet Tracker. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      user: null,
      isAuthenticated: false
    };
  },
  created() {
    // Check if user is authenticated on page load
    this.checkAuth();
  },
  methods: {
    async checkAuth() {
      try {
        const response = await axios.get('/api/auth/check');
        if (response.data.authenticated) {
          this.isAuthenticated = true;
          this.user = response.data.user;
        } else {
          this.isAuthenticated = false;
          this.user = null;
        }
      } catch (error) {
        console.error('Authentication check failed', error);
        this.isAuthenticated = false;
        this.user = null;
      }
    },
    async logout() {
      try {
        await axios.get('/api/auth/logout');
        this.isAuthenticated = false;
        this.user = null;
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout failed', error);
      }
    }
  }
};
</script>

<style>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

footer {
  margin-top: auto;
}
</style>
