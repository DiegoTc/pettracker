<template>
  <div class="app-layout">
    <!-- Top Navigation Bar -->
    <nav class="top-nav">
      <div class="nav-container">
        <div class="nav-logo">
          <router-link to="/">
            <span class="brand-icon"><i class="bi bi-shield-check"></i></span>
            <span class="brand-name">PetTracker</span>
          </router-link>
        </div>
        
        <div class="nav-links">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <i class="bi bi-house-door"></i>
            <span>Home</span>
          </router-link>
          
          <router-link to="/pets" class="nav-link" :class="{ active: $route.path.startsWith('/pets') }">
            <i class="bi bi-heart"></i>
            <span>Pets</span>
          </router-link>
          
          <router-link to="/devices" class="nav-link" :class="{ active: $route.path.startsWith('/devices') }">
            <i class="bi bi-cpu"></i>
            <span>Devices</span>
          </router-link>
          
          <router-link to="/map" class="nav-link" :class="{ active: $route.path === '/map' }">
            <i class="bi bi-geo-alt"></i>
            <span>Map</span>
          </router-link>
          
          <router-link to="/reports" class="nav-link" :class="{ active: $route.path === '/reports' }">
            <i class="bi bi-bar-chart"></i>
            <span>Reports</span>
          </router-link>
          
          <router-link to="/api-test" class="nav-link api-test-link" :class="{ active: $route.path === '/api-test' }">
            <i class="bi bi-wrench-adjustable"></i>
            <span>API Test</span>
          </router-link>
        </div>
        
        <div class="nav-actions">
          <div class="user-menu" @click="toggleUserMenu">
            <div class="user-avatar">
              <img v-if="user && user.profilePicture" :src="user.profilePicture" alt="User">
              <i v-else class="bi bi-person-circle"></i>
            </div>
            <span v-if="user" class="user-name">{{ user.name }}</span>
            <i class="bi bi-chevron-down"></i>
            
            <div v-if="showUserMenu" class="dropdown-menu">
              <router-link to="/profile" class="dropdown-item">
                <i class="bi bi-person"></i> Profile
              </router-link>
              <router-link to="/settings" class="dropdown-item">
                <i class="bi bi-gear"></i> Settings
              </router-link>
              <div class="dropdown-divider"></div>
              <a href="#" class="dropdown-item" @click.prevent="logout">
                <i class="bi bi-box-arrow-right"></i> Logout
              </a>
            </div>
          </div>
        </div>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
      <div class="container">
        <slot></slot>
      </div>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-logo">
            <span class="brand-icon"><i class="bi bi-shield-check"></i></span>
            <span class="brand-name">PetTracker</span>
          </div>
          <div class="footer-copyright">
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

/* Top Navigation */
.top-nav {
  background-color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.nav-logo a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: var(--text);
}

.brand-icon {
  font-size: 24px;
  color: var(--primary);
  margin-right: 8px;
}

.brand-name {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
  font-size: 20px;
}

.nav-links {
  display: flex;
  gap: 8px;
}

.nav-link {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-decoration: none;
  color: var(--text-light);
  padding: 8px 16px;
  border-radius: var(--radius);
  transition: all 0.2s ease;
}

.nav-link i {
  font-size: 20px;
  margin-bottom: 4px;
}

.nav-link span {
  font-size: 12px;
  font-weight: 500;
}

.nav-link:hover, .nav-link.active {
  color: var(--primary);
  background-color: var(--primary-light);
}

.api-test-link {
  margin-left: 8px;
  background-color: #f0f5ff;
  border: 1px dashed #99b3ff;
}

.nav-actions {
  display: flex;
  align-items: center;
}

.user-menu {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius);
  position: relative;
}

.user-menu:hover {
  background-color: var(--background);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--primary-light);
  color: var(--primary);
  margin-right: 8px;
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-avatar i {
  font-size: 22px;
}

.user-name {
  font-weight: 500;
  margin-right: 8px;
  font-size: 14px;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: white;
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  min-width: 200px;
  margin-top: 8px;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  text-decoration: none;
  color: var(--text);
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: var(--background);
}

.dropdown-divider {
  height: 1px;
  background-color: var(--border);
  margin: 4px 0;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 32px 0;
  background-color: var(--background);
}

/* Footer */
.footer {
  background-color: white;
  border-top: 1px solid var(--border);
  padding: 24px 0;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.footer-logo {
  display: flex;
  align-items: center;
}

.footer-copyright {
  font-size: 14px;
  color: var(--text-light);
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .nav-container {
    height: auto;
    flex-direction: column;
    padding: 16px;
  }
  
  .nav-logo {
    margin-bottom: 16px;
  }
  
  .nav-links {
    width: 100%;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  
  .nav-link {
    padding: 8px;
  }
  
  .user-name {
    display: none;
  }
  
  .footer-content {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}
</style>