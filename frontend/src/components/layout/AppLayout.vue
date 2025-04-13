<template>
  <div class="app-layout">
    <!-- Top Navigation Bar -->
    <nav class="navbar navbar-expand-lg bg-white py-2 mb-4">
      <div class="container">
        <router-link to="/" class="navbar-brand d-flex align-items-center">
          <i class="bi bi-shield-check me-2 text-primary"></i>
          <span class="fw-bold">PetTracker</span>
        </router-link>
        
        <div class="d-flex justify-content-center flex-grow-1">
          <div class="nav-buttons text-center">
            <router-link to="/" class="nav-button px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path === '/' }">
              <div class="nav-icon mb-1">
                <i class="bi bi-house-door"></i>
              </div>
              <div class="nav-text">Home</div>
            </router-link>
            
            <router-link to="/pets" class="nav-button px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path.startsWith('/pets') }">
              <div class="nav-icon mb-1">
                <i class="bi bi-heart"></i>
              </div>
              <div class="nav-text">Pets</div>
            </router-link>
            
            <router-link to="/devices" class="nav-button px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path.startsWith('/devices') }">
              <div class="nav-icon mb-1">
                <i class="bi bi-cpu"></i>
              </div>
              <div class="nav-text">Devices</div>
            </router-link>
            
            <router-link to="/map" class="nav-button px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path === '/map' }">
              <div class="nav-icon mb-1">
                <i class="bi bi-geo-alt"></i>
              </div>
              <div class="nav-text">Map</div>
            </router-link>
            
            <router-link to="/reports" class="nav-button px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path === '/reports' }">
              <div class="nav-icon mb-1">
                <i class="bi bi-bar-chart"></i>
              </div>
              <div class="nav-text">Reports</div>
            </router-link>
            
            <router-link to="/api-test" class="nav-button api-test px-4 mx-1 text-decoration-none text-center" :class="{ active: $route.path === '/api-test' }">
              <div class="nav-icon mb-1">
                <i class="bi bi-wrench-adjustable"></i>
              </div>
              <div class="nav-text">API Test</div>
            </router-link>
          </div>
        </div>
        
        <div class="user-profile d-flex align-items-center">
          <div class="user-avatar rounded-circle bg-light d-flex align-items-center justify-content-center me-2">
            <i class="bi bi-person-circle text-primary"></i>
          </div>
          <span class="user-name">{{ user.name }}</span>
          <div class="dropdown ms-2">
            <button class="btn btn-sm btn-outline-secondary dropdown-toggle" type="button" id="userMenuDropdown" data-bs-toggle="dropdown" aria-expanded="false">
              <i class="bi bi-gear"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuDropdown">
              <li>
                <button class="dropdown-item" @click="logout" :disabled="loading">
                  <span v-if="loading"><i class="bi bi-hourglass-split me-2"></i>Signing Out...</span>
                  <span v-else><i class="bi bi-box-arrow-right me-2"></i>Sign Out</span>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content bg-light">
      <div class="container py-4">
        <slot></slot>
      </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer py-4 bg-white border-top">
      <div class="container">
        <div class="d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <i class="bi bi-shield-check me-2 text-primary"></i>
            <span class="fw-bold">PetTracker</span>
          </div>
          <div class="text-muted small">
            &copy; {{ new Date().getFullYear() }} PetTracker. All rights reserved.
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { authAPI } from '@/services/api';

export default {
  name: 'AppLayout',
  data() {
    return {
      showUserMenu: false,
      user: {
        name: 'User',
        profilePicture: null,
        email: '',
        id: null
      },
      loading: false
    }
  },
  
  async mounted() {
    // Fetch user information when component is mounted
    this.fetchUserInfo();
  },
  
  methods: {
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    
    async fetchUserInfo() {
      // Only fetch user info if we have a token
      if (!localStorage.getItem('access_token')) {
        console.log('No authentication token available, skipping user fetch');
        return;
      }
      
      try {
        this.loading = true;
        const response = await authAPI.getUser();
        
        if (response.data) {
          // Update user data
          this.user = {
            name: response.data.username || response.data.first_name || 'User',
            email: response.data.email || '',
            id: response.data.id,
            profilePicture: response.data.profile_picture || null
          };
          
          console.log('User information loaded successfully');
        }
      } catch (error) {
        console.error('Error fetching user information:', error);
        
        // If we get an authentication error, redirect to login
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      } finally {
        this.loading = false;
      }
    },
    
    async logout() {
      // Set loading state
      this.loading = true;
      
      try {
        // Call the logout endpoint
        await authAPI.logout();
        
        // Clear authentication data from localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('is_authenticated');
        
        console.log('User signed out successfully');
        
        // Redirect to login page
        this.$router.push('/login');
      } catch (error) {
        console.error('Error during sign out:', error);
        
        // Even if the API call fails, clear local storage and redirect
        localStorage.removeItem('access_token');
        localStorage.removeItem('is_authenticated');
        this.$router.push('/login');
      } finally {
        // Reset loading state - though it won't be visible as we're redirecting
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.nav-buttons {
  display: flex;
  align-items: center;
}

.nav-button {
  color: #666;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-radius: 6px;
  padding: 10px 12px;
  transition: all 0.2s;
}

.nav-button:hover {
  background-color: #f0f7ff;
  color: #0d6efd;
}

.nav-button.active {
  background-color: #f0f7ff;
  color: #0d6efd;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 12px;
  font-weight: 500;
}

.api-test {
  border: 1px dashed #c5d5f5;
  background-color: #f0f7ff;
}

.user-avatar {
  width: 32px;
  height: 32px;
}

.user-name {
  font-weight: 500;
  font-size: 14px;
}

.main-content {
  flex: 1;
  background-color: #f5f7fb;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .nav-buttons {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-button {
    margin-bottom: 8px;
  }
  
  .user-name {
    display: none;
  }
}
</style>