<template>
  <div class="app-container">
    <!-- Top Bar -->
    <header class="app-header">
      <div class="header-logo">
        <i class="bi bi-heart-fill"></i>
        <span>PetTracker</span>
      </div>
      
      <nav class="header-nav">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          Dashboard
        </router-link>
        
        <router-link to="/pets" class="nav-link" :class="{ active: $route.path.startsWith('/pets') }">
          My Pets
        </router-link>
        
        <router-link to="/devices" class="nav-link" :class="{ active: $route.path.startsWith('/devices') }">
          Devices
        </router-link>
        
        <router-link to="/map" class="nav-link" :class="{ active: $route.path === '/map' }">
          Map
        </router-link>
        
        <router-link to="/reports" class="nav-link" :class="{ active: $route.path === '/reports' }">
          Reports
        </router-link>
        
        <router-link to="/api-test" class="nav-link" :class="{ active: $route.path === '/api-test' }">
          API Test
        </router-link>
      </nav>
      
      <div class="header-actions">
        <button class="action-button">
          <i class="bi bi-search"></i>
        </button>
        
        <button class="action-button">
          <i class="bi bi-bell"></i>
          <span v-if="false" class="badge">3</span>
        </button>
        
        <div class="dropdown">
          <button class="action-button" id="userMenuDropdown" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="bi bi-gear"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userMenuDropdown">
            <li><h6 class="dropdown-header">User Options</h6></li>
            <li><a class="dropdown-item" href="#"><i class="bi bi-person me-2"></i>Profile</a></li>
            <li><a class="dropdown-item" href="#"><i class="bi bi-sliders me-2"></i>Settings</a></li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <button class="dropdown-item text-danger" @click="logout" :disabled="loading">
                <span v-if="loading"><i class="bi bi-hourglass-split me-2"></i>Signing Out...</span>
                <span v-else><i class="bi bi-box-arrow-right me-2"></i>Sign Out</span>
              </button>
            </li>
          </ul>
        </div>
        
        <div class="user-profile">
          <div v-if="user.profilePicture" class="avatar">
            <img :src="user.profilePicture" alt="User profile">
          </div>
          <div v-else class="avatar">
            {{ userInitials }}
          </div>
        </div>
        
        <!-- Direct logout button (only visible on mobile) -->
        <button 
          class="mobile-logout-btn btn btn-danger btn-sm" 
          @click="logout" 
          :disabled="loading"
          title="Sign out"
        >
          <i class="bi bi-box-arrow-right"></i>
          <span class="ms-1">Sign Out</span>
        </button>
      </div>
    </header>
    
    <!-- Main Content -->
    <main class="main-content">
      <slot></slot>
    </main>
    
    <!-- Footer -->
    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-logo">
            <i class="bi bi-heart-fill"></i>
            <span>PetTracker</span>
          </div>
          <div class="copyright">
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
  
  computed: {
    /**
     * Generates user initials for the avatar when no profile picture is available
     * Uses the first letter of the username, or "U" as fallback
     */
    userInitials() {
      if (!this.user.name || this.user.name === 'User') {
        // Use email if name is not available
        if (this.user.email && this.user.email.length > 0) {
          return this.user.email.charAt(0).toUpperCase();
        }
        return 'U';
      }
      
      // Get first letter of each word
      const nameParts = this.user.name.split(' ');
      if (nameParts.length === 1) {
        return nameParts[0].charAt(0).toUpperCase();
      }
      
      // Get first and last part for first and last name
      return (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
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
    
    /**
     * Securely logs out the user by:
     * 1. Notifying the backend to terminate the session and invalidate the JWT token
     * 2. Clearing all authentication data from the browser
     * 3. Redirecting to the login page
     */
    async logout() {
      // Set loading state to show user feedback
      this.loading = true;
      
      try {
        // Create a timestamp to measure logout performance
        const startTime = Date.now();
        
        // Call the logout endpoint with proper error handling
        const response = await authAPI.logout();
        
        // Log success message with timing information
        console.log(`Sign out successful (${Date.now() - startTime}ms)`, response.data);
        
        // Clear ALL authentication and user-related data
        this.clearAuthData();
        
        // Show success message before redirecting (if needed)
        // Could be implemented with a toast notification
        
        // Redirect to login page with a small delay to allow UI updates
        setTimeout(() => {
          this.$router.push('/login');
        }, 100);
      } catch (error) {
        // Log detailed error for debugging
        console.error('Error during sign out:', error);
        
        // Even if the API call fails, still clear auth data and redirect
        // This ensures the user can log out even if backend is unreachable
        this.clearAuthData();
        
        // Redirect to login page with error parameter
        this.$router.push('/login?logout_error=true');
      } finally {
        // Reset loading state
        this.loading = false;
      }
    },
    
    /**
     * Clear all authentication and user data from browser storage
     * This method centralizes the cleanup logic for security
     */
    clearAuthData() {
      // Clear JWT token and auth state
      localStorage.removeItem('access_token');
      localStorage.removeItem('is_authenticated');
      
      // Clear any additional user data that might be stored
      localStorage.removeItem('login_redirect');
      sessionStorage.removeItem('user_data');
      
      // Clear all cookies related to authentication by setting expiry in the past
      // This is important for enhanced security
      document.cookie.split(';').forEach(cookie => {
        const [name] = cookie.trim().split('=');
        document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
      });
      
      console.log('Authentication data cleared successfully');
    }
  }
}
</script>

<style scoped>
/* Layout */
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Top Bar */
.app-header {
  background-color: var(--background);
  box-shadow: var(--shadow-sm);
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
}

.header-logo {
  display: flex;
  align-items: center;
  color: var(--primary);
  font-size: 22px;
  font-weight: 700;
  font-family: 'Montserrat', sans-serif;
  margin-right: 40px;
}

.header-logo i {
  margin-right: 10px;
  font-size: 24px;
}

.header-nav {
  display: flex;
  margin-right: auto;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 0 15px;
  height: 70px;
  color: var(--text);
  text-decoration: none;
  font-weight: 500;
  font-size: 15px;
  position: relative;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: var(--primary);
}

.nav-link.active {
  color: var(--primary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 15px;
  right: 15px;
  height: 3px;
  background-color: var(--primary);
  border-radius: 3px 3px 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
}

.action-button {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  color: var(--text-light);
  border: none;
  cursor: pointer;
  margin-left: 10px;
  transition: background-color 0.3s ease, color 0.3s ease;
  position: relative;
}

.action-button:hover {
  background-color: rgba(33, 150, 243, 0.1);
  color: var(--primary);
}

.badge {
  position: absolute;
  top: -2px;
  right: -2px;
  background-color: var(--secondary);
  color: white;
  font-size: 10px;
  font-weight: 600;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-profile {
  display: flex;
  align-items: center;
  margin-left: 15px;
  cursor: pointer;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #E3F2FD;
  color: var(--primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Montserrat', sans-serif;
  overflow: hidden;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Main Content */
.main-content {
  margin-top: 70px;
  padding: 30px;
  flex: 1;
  background-color: #f5f7fb;
}

/* Dropdown Menu */
.dropdown-menu {
  border-radius: var(--radius);
  box-shadow: var(--shadow-md);
  border: none;
  padding: 8px 0;
  min-width: 180px;
  margin-top: 8px;
}

.dropdown-header {
  font-family: 'Montserrat', sans-serif;
  color: var(--text-light);
  font-weight: 600;
  padding: 8px 16px;
  font-size: 12px;
}

.dropdown-item {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  color: var(--text);
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #F5F7FB;
}

.dropdown-item i {
  margin-right: 10px;
  font-size: 16px;
  color: var(--text-light);
}

.dropdown-divider {
  margin: 4px 0;
  border-top: 1px solid var(--border);
}

/* Footer */
.footer {
  background-color: var(--background);
  border-top: 1px solid var(--border);
  padding: 24px 0;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-logo {
  display: flex;
  align-items: center;
  color: var(--primary);
  font-weight: 600;
}

.footer-logo i {
  margin-right: 8px;
}

.copyright {
  color: var(--text-light);
  font-size: 14px;
}

/* Mobile logout button - only visible on small screens */
.mobile-logout-btn {
  display: none;
}

/* Responsive Adjustments */
@media (max-width: 992px) {
  .header-nav {
    display: none;
  }
  
  .header-logo {
    margin-right: auto;
  }
}

@media (max-width: 576px) {
  .app-header {
    padding: 0 16px;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
  }
  
  .main-content {
    padding: 20px 15px;
  }
  
  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 10px;
  }
  
  .mobile-logout-btn {
    display: flex;
    margin-left: 10px;
    padding: 0 10px;
    height: 36px;
  }
  
  .mobile-logout-btn span {
    display: none;
  }
}
</style>