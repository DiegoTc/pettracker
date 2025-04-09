import { createRouter, createWebHistory } from 'vue-router';
import { authAPI } from '../services/api';

// Lazy-loaded route components
const Home = () => import('../views/Home.vue');
const Login = () => import('../views/Login.vue');
const Pets = () => import('../views/Pets.vue');
const PetForm = () => import('../views/PetForm.vue');
const Devices = () => import('../views/Devices.vue');
const DeviceForm = () => import('../views/DeviceForm.vue');
const NotFound = () => import('../views/NotFound.vue');

// Routes configuration
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guestOnly: true }
  },
  {
    path: '/pets',
    name: 'Pets',
    component: Pets,
    meta: { requiresAuth: true }
  },
  {
    path: '/pets/new',
    name: 'NewPet',
    component: PetForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/pets/:id/edit',
    name: 'EditPet',
    component: PetForm,
    props: true,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices',
    name: 'Devices',
    component: Devices,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices/new',
    name: 'NewDevice',
    component: DeviceForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/devices/:id/edit',
    name: 'EditDevice',
    component: DeviceForm,
    props: true,
    meta: { requiresAuth: true }
  },
  // Special route to handle authentication callback
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('../views/AuthCallback.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard to handle authentication
router.beforeEach(async (to, from, next) => {
  // Check for token-based authentication
  const hasToken = !!localStorage.getItem('access_token');
  
  // For routes that require authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (hasToken) {
      // If we have a token, allow access
      next();
    } else {
      try {
        // Fallback to cookie-based session check
        const response = await authAPI.checkAuth();
        if (response.data.authenticated) {
          // User is authenticated via session cookie, proceed
          // We'll get a JWT token in App.vue
          next();
        } else {
          // Not authenticated, redirect to login
          next({ 
            name: 'Login', 
            query: { redirect: to.fullPath } 
          });
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        // On error, assume not authenticated
        next({ 
          name: 'Login', 
          query: { redirect: to.fullPath } 
        });
      }
    }
  } 
  // For routes that are only for guests (not logged in)
  else if (to.matched.some(record => record.meta.guestOnly)) {
    if (hasToken) {
      // User has a token, redirect to home
      next({ name: 'Home' });
    } else {
      try {
        // Check if user is authenticated via session
        const response = await authAPI.checkAuth();
        if (response.data.authenticated) {
          // User is authenticated via session, redirect to home
          next({ name: 'Home' });
        } else {
          // Not authenticated, proceed to guest route
          next();
        }
      } catch (error) {
        // On error, assume not authenticated and proceed
        next();
      }
    }
  } 
  // All other routes
  else {
    next();
  }
});

export default router;
