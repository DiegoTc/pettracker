import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import Pets from '../views/Pets.vue';

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
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// Navigation guard for authentication (to be implemented)
router.beforeEach((to, from, next) => {
  // For now, allow all navigation
  next();
});

export default router;