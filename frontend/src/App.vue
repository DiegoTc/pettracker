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

/* CSS Variables - From Mockup #2 */
:root {
  --primary: #2196F3;
  --primary-light: #64B5F6;
  --primary-dark: #1976D2;
  --secondary: #FF4081;
  --success: #4CAF50;
  --warning: #FFC107;
  --danger: #F44336;
  --background: #FFFFFF;
  --card-bg: #FFFFFF;
  --border: #EEEEEE;
  --text: #212121;
  --text-light: #757575;
  --text-lighter: #9E9E9E;
  --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 5px 20px rgba(0, 0, 0, 0.08);
  --shadow-lg: 0 10px 30px rgba(0, 0, 0, 0.12);
  --radius: 12px;
}

/* Global Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f7fb;
  color: var(--text);
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Montserrat', sans-serif;
  color: var(--text);
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 30px;
  color: var(--text);
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text);
}

/* Override Bootstrap styles to match mockup #2 */
.form-label {
  font-weight: 500;
  color: var(--text);
  margin-bottom: 0.5rem;
}

.form-control, .form-select {
  border-color: var(--border);
  padding: 0.75rem 1rem;
  color: #333333;
  border-radius: var(--radius);
}

.form-control:focus, .form-select:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 0.25rem rgba(33, 150, 243, 0.25);
}

/* Modern Clean Fields input styling */
.input-wrapper {
  position: relative;
  width: 100%;
}

.input-wrapper .form-control,
.input-wrapper .form-select {
  border: 1px solid var(--border);
  background-color: #ffffff;
  color: #333333;
  transition: all 0.2s ease;
}

.input-wrapper .form-control:focus,
.input-wrapper .form-select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.15);
}

/* Style for dropdown options */
.form-select option {
  color: #333333;
  background-color: #ffffff;
}

.card {
  border-radius: var(--radius);
  background-color: var(--card-bg);
  box-shadow: var(--shadow-sm);
  border: none;
  overflow: hidden;
}

.card-title {
  font-weight: 600;
  color: var(--text);
}

.card-body {
  padding: 24px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 42px;
  padding: 0 20px;
  border-radius: 21px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
  box-shadow: 0 4px 10px rgba(33, 150, 243, 0.3);
}

.btn-secondary {
  background-color: var(--secondary);
  color: white;
}

.btn-secondary:hover {
  background-color: #e91e63;
  box-shadow: 0 4px 10px rgba(255, 64, 129, 0.3);
}

.btn-success {
  background-color: var(--success);
  color: white;
}

.btn-success:hover {
  background-color: #388e3c;
  box-shadow: 0 4px 10px rgba(76, 175, 80, 0.3);
}

.btn-warning {
  background-color: var(--warning);
  color: white;
}

.btn-warning:hover {
  background-color: #ffa000;
  box-shadow: 0 4px 10px rgba(255, 193, 7, 0.3);
}

.btn-danger {
  background-color: var(--danger);
  color: white;
}

.btn-danger:hover {
  background-color: #d32f2f;
  box-shadow: 0 4px 10px rgba(244, 67, 54, 0.3);
}

.btn-outline-danger {
  background-color: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}

.btn-outline-danger:hover {
  background-color: var(--danger);
  color: white;
  box-shadow: 0 4px 10px rgba(244, 67, 54, 0.3);
}

.btn-sm {
  height: 36px;
  padding: 0 15px;
  font-size: 13px;
}

.btn-lg {
  height: 48px;
  padding: 0 24px;
  font-size: 15px;
}

.btn i {
  margin-right: 8px;
}

/* Spinner */
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

/* Utility Classes */
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
</style>