<template>
  <div class="quick-card">
    <div class="quick-icon">
      <i :class="icon"></i>
    </div>
    <h3 class="quick-title">{{ title }}</h3>
    <p class="quick-text">{{ description }}</p>
    <button 
      class="btn" 
      :class="`btn-${buttonType}`" 
      @click="$emit('action')"
    >
      <i v-if="buttonIcon" :class="buttonIcon"></i> {{ buttonText }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'ActionCard',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    buttonText: {
      type: String,
      required: true
    },
    buttonIcon: {
      type: String,
      default: null
    },
    buttonType: {
      type: String,
      default: 'primary',
      validator: value => ['primary', 'secondary', 'success', 'warning'].includes(value)
    }
  }
}
</script>