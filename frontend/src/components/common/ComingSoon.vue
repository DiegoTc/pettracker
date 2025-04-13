<template>
  <div class="coming-soon">
    <div class="icon-container">
      <i class="bi bi-rocket-takeoff"></i>
    </div>
    <h4 class="title">{{ title }}</h4>
    <p class="description">{{ description }}</p>
  </div>
</template>

<script>
export default {
  name: 'ComingSoon',
  props: {
    title: {
      type: String,
      default: 'Coming Soon'
    },
    description: {
      type: String,
      default: 'This feature is currently under development and will be available soon.'
    }
  }
}
</script>

<style scoped>
.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
  background: linear-gradient(to bottom right, rgba(245, 247, 251, 0.9), rgba(233, 236, 239, 0.7));
  border-radius: var(--radius);
  height: 100%;
  min-height: 300px;
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
}

.coming-soon:before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zM32 63c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm57-13c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%232196f3' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.8;
  z-index: 0;
}

.icon-container {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  color: var(--primary);
  position: relative;
  z-index: 1;
  animation: float 3s ease-in-out infinite;
  text-shadow: 0 10px 20px rgba(33, 150, 243, 0.15);
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
  100% {
    transform: translateY(0px);
  }
}

.title {
  font-size: 1.75rem;
  margin-bottom: 1rem;
  color: var(--text);
  font-weight: 700;
  position: relative;
  z-index: 1;
}

.description {
  color: var(--text-light);
  max-width: 450px;
  margin: 0 auto;
  font-size: 1.1rem;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

@media (max-width: 768px) {
  .coming-soon {
    padding: 2.5rem 1.5rem;
    min-height: 250px;
  }
  
  .icon-container {
    font-size: 3rem;
  }
  
  .title {
    font-size: 1.5rem;
  }
  
  .description {
    font-size: 1rem;
  }
}
</style>