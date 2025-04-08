<template>
  <div id="app">
    <!-- Navigation bar for authenticated users -->
    <nav v-if="isAuthenticated" class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          Pet Tracker
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">
                <i class="bi bi-house-door me-1"></i> Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/pets">
                <i class="bi bi-heart me-1"></i> My Pets
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/devices">
                <i class="bi bi-cpu me-1"></i> Devices
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/map">
                <i class="bi bi-geo-alt me-1"></i> Map
              </router-link>
            </li>
          </ul>
          
          <div class="navbar-nav">
            <div class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <img 
                  v-if="user && user.profile_picture" 
                  :src="user.profile_picture" 
                  alt="Profile" 
                  class="avatar-img me-1"
                >
                <i v-else class="bi bi-person-circle me-1"></i>
                {{ user ? (user.full_name || user.username) : 'Account' }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <router-link class="dropdown-item" to="/profile">
                    <i class="bi bi-person me-2"></i> Profile
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item" to="/settings">
                    <i class="bi bi-gear me-2"></i> Settings
                  </router-link>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="bi bi-box-arrow-right me-2"></i> Logout
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <div class="container mt-4">
      <router-view></router-view>
    </div>
    
    <!-- Footer -->
    <footer class="footer mt-auto py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">© 2025 Pet Tracker. All rights reserved.</span>
      </div>
    </footer>
  </div>
</template>

<script>
import { authAPI } from './services/api';
import { Modal } from 'bootstrap';

export default {
  name: 'App',
  data() {
    return {
      isAuthenticated: false,
      user: null,
      loading: true,
      navbarCollapse: null
    };
  },
  async created() {
    // Check authentication status
    try {
      const authResponse = await authAPI.checkAuth();
      this.isAuthenticated = authResponse.data.authenticated;
      
      if (this.isAuthenticated) {
        // Get user data
        const userResponse = await authAPI.getUser();
        this.user = userResponse.data;
      }
    } catch (error) {
      console.error('Auth check error:', error);
      this.isAuthenticated = false;
    } finally {
      this.loading = false;
    }
  },
  mounted() {
    // Initialize all Bootstrap components
    // Navbar collapse for mobile responsiveness
    this.initBootstrapComponents();
  },
  methods: {
    async logout() {
      try {
        await authAPI.logout();
        this.isAuthenticated = false;
        this.user = null;
        
        // Redirect to login page
        this.$router.push('/login');
      } catch (error) {
        console.error('Logout error:', error);
        alert('Failed to logout. Please try again.');
      }
    },
    initBootstrapComponents() {
      // Get all dropdowns for initialization
      document.querySelectorAll('.dropdown-toggle').forEach(dropdownToggle => {
        new bootstrap.Dropdown(dropdownToggle);
      });
      
      // Initialize collapsible navbar
      const navbarToggler = document.querySelector('.navbar-toggler');
      if (navbarToggler) {
        this.navbarCollapse = new bootstrap.Collapse(document.getElementById('navbarNav'), {
          toggle: false
        });
        
        // Close navbar when a nav link is clicked (mobile view)
        document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
          link.addEventListener('click', () => {
            if (window.innerWidth < 992 && this.navbarCollapse._isShown()) {
              this.navbarCollapse.hide();
            }
          });
        });
      }
    }
  }
};
</script>

<style>
/* Import Bootstrap icons CSS */
@import url("https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css");

/* Global Styles */
html, body {
  height: 100%;
}

body {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.container {
  flex: 1;
}

.footer {
  margin-top: auto;
}

/* Avatar image in navbar */
.avatar-img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  object-fit: cover;
}

/* Add space at the bottom for the footer */
.router-view-container {
  margin-bottom: 70px;
}
</style>
