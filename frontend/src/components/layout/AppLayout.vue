<template>
  <div class="app-container">
    <!-- Top Bar -->
    <header class="app-header">
      <div class="header-logo">
        <i class="bi bi-heart-fill"></i>
        <span>PetTracker</span>
      </div>
      
      <nav class="header-nav">
        <router-link to="/" class="nav-link" :class="{ active: isActive('/') }">
          Dashboard
        </router-link>
        <router-link to="/pets" class="nav-link" :class="{ active: isActive('/pets') }">
          My Pets
        </router-link>
        <router-link to="/devices" class="nav-link" :class="{ active: isActive('/devices') }">
          Devices
        </router-link>
        <router-link to="/map" class="nav-link" :class="{ active: isActive('/map') }">
          Map
        </router-link>
        <router-link to="/reports" class="nav-link" :class="{ active: isActive('/reports') }">
          Reports
        </router-link>
      </nav>
      
      <div class="header-actions">
        <button class="action-button">
          <i class="bi bi-search"></i>
        </button>
        <button class="action-button">
          <i class="bi bi-bell"></i>
          <span class="badge" v-if="unreadNotifications > 0">{{ unreadNotifications }}</span>
        </button>
        <div class="user-profile" @click="toggleUserMenu">
          <div class="avatar">{{ userInitials }}</div>
        </div>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
      <slot></slot>
    </main>

    <!-- User Menu Dropdown (to be implemented) -->
  </div>
</template>

<script>
export default {
  name: 'AppLayout',
  data() {
    return {
      unreadNotifications: 2,
      userMenuOpen: false
    }
  },
  computed: {
    userInitials() {
      // Get user data from store or props when authentication is implemented
      // For now, return placeholder
      return 'JD';
    }
  },
  methods: {
    isActive(route) {
      return this.$route.path === route || this.$route.path.startsWith(route + '/');
    },
    toggleUserMenu() {
      this.userMenuOpen = !this.userMenuOpen;
      // Implement user menu dropdown
    }
  }
}
</script>

<style>
/* Import the theme CSS */
@import '../../assets/styles/pettracker-theme.css';

/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Quicksand:wght@400;500;600&family=Roboto:wght@400;500&display=swap');

/* Import Bootstrap Icons */
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css');
</style>