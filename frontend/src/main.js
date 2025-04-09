import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

// Create and mount the Vue application
const app = createApp(App);

// Use Vue Router
app.use(router);

// Mount the app
app.mount('#app');