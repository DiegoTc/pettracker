<template>
  <div class="card-component" :class="{ 'no-padding': noPadding, [`card-${type}`]: type }">
    <div class="card-header">
      <div class="card-header-left">
        <i v-if="icon" :class="icon"></i>
        <h3 class="card-title">{{ title }}</h3>
      </div>
      <div class="card-header-right">
        <button v-if="showRefresh" @click="$emit('refresh')" class="card-action refresh">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
        <router-link v-if="showMore" :to="moreLink" class="card-action more">
          <span>View all</span>
          <i class="bi bi-chevron-right"></i>
        </router-link>
      </div>
    </div>
    <div class="card-body">
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CardComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    icon: {
      type: String,
      default: null
    },
    type: {
      type: String,
      default: 'default',
      validator: value => ['default', 'primary', 'map', 'table'].includes(value)
    },
    showRefresh: {
      type: Boolean,
      default: false
    },
    showMore: {
      type: Boolean,
      default: false
    },
    moreLink: {
      type: String,
      default: '#'
    },
    noPadding: {
      type: Boolean,
      default: false
    }
  }
}
</script>

<style scoped>
.card-component {
  background-color: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.card-component:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header-left {
  display: flex;
  align-items: center;
}

.card-header-left i {
  margin-right: 10px;
  font-size: 20px;
  color: var(--primary);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
}

.card-header-right {
  display: flex;
  align-items: center;
}

.card-action {
  background-color: transparent;
  border: none;
  color: var(--text-light);
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  display: flex;
  align-items: center;
}

.refresh {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.more {
  text-decoration: none;
  display: flex;
  align-items: center;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 500;
}

.more span {
  margin-right: 6px;
}

.card-action:hover {
  background-color: rgba(33, 150, 243, 0.1);
  color: var(--primary);
}

.card-body {
  padding: 24px;
  flex: 1;
}

.no-padding .card-body {
  padding: 0;
}

/* Card types */
.card-primary {
  border-top: 4px solid var(--primary);
}

.card-map {
  display: flex;
  flex-direction: column;
}

.card-map .card-body {
  flex: 1;
  padding: 0;
}

.card-table .card-body {
  padding: 0;
}
</style>