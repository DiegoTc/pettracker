<template>
  <router-view />
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&family=Quicksand:wght@400;500;600&family=Roboto:wght@400;500&display=swap');

/* Import Bootstrap Icons */
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css');

/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* Override Bootstrap styles for light theme */
.form-label {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.5rem;
}

.form-control, .form-select {
  border-color: #dee2e6;
  padding: 0.5rem 0.75rem;
  color: #333;
}

.form-control:focus, .form-select:focus {
  border-color: #80bdff;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.25);
}

.card {
  border-radius: 0.5rem;
  background-color: #fff;
}

.card-title {
  font-weight: 600;
  color: #333;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f7fb;
  color: #333;
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Montserrat', sans-serif;
  color: #333;
}

.text-center {
  text-align: center;
}

.my-5 {
  margin-top: 2.5rem;
  margin-bottom: 2.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.ms-2 {
  margin-left: 0.5rem;
}

.btn-sm {
  height: 32px;
  padding: 0 12px;
  font-size: 13px;
}

.spinner-border {
  display: inline-block;
  width: 48px;
  height: 48px;
  border: 4px solid var(--primary);
  border-right-color: transparent;
  border-radius: 50%;
  animation: spinner-border 0.75s linear infinite;
}

@keyframes spinner-border {
  to { transform: rotate(360deg); }
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.btn-outline-danger {
  background-color: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}

.btn-outline-danger:hover {
  background-color: var(--danger);
  color: white;
}
</style>