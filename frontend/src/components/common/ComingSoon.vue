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
  padding: 2rem;
  text-align: center;
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  height: 100%;
  min-height: 200px;
}

.icon-container {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #6c757d;
}

.title {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #495057;
}

.description {
  color: #6c757d;
  max-width: 400px;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .coming-soon {
    padding: 1.5rem;
    min-height: 150px;
  }
  
  .icon-container {
    font-size: 2.5rem;
  }
  
  .title {
    font-size: 1.25rem;
  }
}
</style>