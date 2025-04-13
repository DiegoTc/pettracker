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
          <span class="user-name">John D</span>
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
export default {
  name: 'AppLayout',
  data() {
    return {
      showUserMenu: false,
      user: {
        name: 'John Doe',
        profilePicture: null
      }
    }
  },
  methods: {
    toggleUserMenu() {
      this.showUserMenu = !this.showUserMenu;
    },
    logout() {
      // Handle logout logic
      console.log('User logged out');
      this.$router.push('/login');
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