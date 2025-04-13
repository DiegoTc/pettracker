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
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content, .error-content, .empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  text-align: center;
  width: 100%;
}

.spinner-container {
  margin-bottom: 0.5rem;
}

.loading-message, .error-message, .empty-message {
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
}

.error-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.empty-icon {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: #dee2e6;
}
</style>