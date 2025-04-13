<template>
  <div class="loading-state" :class="{ 'full-height': fullHeight }">
    <div v-if="loading" class="loading-content">
      <div class="spinner-container">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      <p v-if="message" class="loading-message">{{ message }}</p>
    </div>
    
    <div v-else-if="error" class="error-content">
      <div class="error-icon">
        <i class="bi bi-exclamation-triangle-fill text-warning"></i>
      </div>
      <p class="error-message">{{ errorMessage }}</p>
      <button v-if="retryEnabled" @click="$emit('retry')" class="btn btn-sm btn-outline-primary mt-2">
        <i class="bi bi-arrow-clockwise me-1"></i>
        Try Again
      </button>
    </div>
    
    <div v-else-if="isEmpty" class="empty-content">
      <div class="empty-icon">
        <i class="bi bi-inbox text-muted"></i>
      </div>
      <p class="empty-message">{{ emptyMessage }}</p>
    </div>
    
    <div v-else class="content-loaded">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingState',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: Boolean,
      default: false
    },
    errorMessage: {
      type: String,
      default: 'An error occurred while loading data.'
    },
    isEmpty: {
      type: Boolean,
      default: false
    },
    emptyMessage: {
      type: String,
      default: 'No data available.'
    },
    retryEnabled: {
      type: Boolean,
      default: true
    },
    message: {
      type: String,
      default: 'Loading...'
    },
    fullHeight: {
      type: Boolean,
      default: false
    }
  },
  emits: ['retry']
}
</script>

<style scoped>
.loading-state {
  width: 100%;
  position: relative;
}

.loading-state.full-height {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content, .error-content, .empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  width: 100%;
  background-color: rgba(245, 247, 251, 0.5);
  border-radius: var(--radius);
}

.spinner-container {
  margin-bottom: 1rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  border-width: 0.25rem;
}

.loading-message, .error-message, .empty-message {
  margin-top: 1rem;
  color: var(--text-light);
  font-size: 1rem;
  max-width: 350px;
  line-height: 1.5;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--warning);
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: var(--text-lighter);
}

.btn-outline-primary {
  border: 1px solid var(--primary);
  color: var(--primary);
  background-color: transparent;
  padding: 0.5rem 1rem;
  font-weight: 500;
  border-radius: var(--radius);
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  background-color: var(--primary);
  color: white;
  box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
}
</style>