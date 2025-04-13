import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Pets from '../views/Pets.vue';
import ApiTestComponent from '../views/ApiTest.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/pets',
    name: 'Pets',
    component: Pets
  },
  {
    path: '/pets/new',
    name: 'NewPet',
    component: () => import('../views/PetForm.vue')
  },
  {
    path: '/pets/:id',
    name: 'PetDetails',
    component: () => import('../views/PetDetails.vue')
  },
  {
    path: '/pets/:id/edit',
    name: 'EditPet',
    component: () => import('../views/PetForm.vue')
  },
  {
    path: '/devices',
    name: 'Devices',
    component: () => import('../views/Devices.vue')
  },
  {
    path: '/devices/new',
    name: 'NewDevice',
    component: () => import('../views/DeviceForm.vue')
  },
  {
    path: '/devices/:id/edit',
    name: 'EditDevice',
    component: () => import('../views/DeviceForm.vue')
  },
  {
    path: '/map',
    name: 'Map',
    component: () => import('../views/Map.vue')
  },
  {
    path: '/reports',
    name: 'Reports',
    component: () => import('../views/Reports.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/dev-token',
    name: 'DevToken',
    component: () => import('../views/DevToken.vue')
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('../views/AuthCallback.vue')
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: ApiTestComponent
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication
router.beforeEach((to, from, next) => {
  // Skip auth check for login, callback, dev-token and api-test routes
  const publicPages = ['/login', '/auth/callback', '/dev-token', '/api-test'];
  const authRequired = !publicPages.includes(to.path);
  const loggedIn = localStorage.getItem('access_token');
  
  if (authRequired && !loggedIn) {
    // Store the intended destination for redirect after login
    localStorage.setItem('login_redirect', to.fullPath);
    return next('/login');
  }
  
  next();
});

export default router;
