<template>
  <div class="stat-card">
    <div class="stat-icon">
      <i :class="icon"></i>
    </div>
    <div class="stat-content">
      <h3>{{ title }}</h3>
      <p class="stat-value">{{ value }}</p>
      <p 
        v-if="change" 
        class="stat-change" 
        :class="{ 
          'positive': changeType === 'positive', 
          'negative': changeType === 'negative',
          'neutral': changeType === 'neutral'
        }"
      >
        <i v-if="changeType === 'positive'" class="bi bi-arrow-up-right"></i>
        <i v-if="changeType === 'negative'" class="bi bi-arrow-down-right"></i>
        {{ change }}
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      required: true
    },
    change: {
      type: String,
      default: null
    },
    changeType: {
      type: String,
      validator: value => ['positive', 'negative', 'neutral'].includes(value),
      default: 'neutral'
    }
  }
}
</script>