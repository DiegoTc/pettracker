import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import routes from './router/index.js';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

// Create Vue Router instance
const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Create and mount the Vue application
const app = createApp(App);
app.use(router);
app.mount('#app');