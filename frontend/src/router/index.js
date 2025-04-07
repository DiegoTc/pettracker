// Import route components
import Home from '../views/Home.vue';
import Login from '../views/Login.vue';
import Pets from '../views/Pets.vue';
import PetForm from '../views/PetForm.vue';
import Devices from '../views/Devices.vue';
import DeviceForm from '../views/DeviceForm.vue';
import NotFound from '../views/NotFound.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
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
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
];

export default routes;