<template>
  <app-layout>
    <div class="page-header">
      <div class="d-flex align-items-center">
        <button class="btn btn-outline-secondary me-3" @click="$router.go(-1)">
          <i class="bi bi-arrow-left"></i>
        </button>
        <h1 class="page-title mb-0">{{ isEditMode ? 'Edit Device' : 'Add New Device' }}</h1>
      </div>
    </div>

    <div class="form-container">
      <card-component :title="isEditMode ? 'Edit Device Information' : 'Device Information'" icon="bi bi-pencil-square">
        <!-- Global Error Message -->
        <div v-if="globalError" class="alert alert-danger mb-3">
          {{ globalError }}
        </div>
        
        <form @submit.prevent="saveDevice">
          <div class="form-row">
            <div class="form-group">
              <div class="label-with-tooltip">
                <label for="imei" class="form-label">
                  IMEI Number <span class="text-danger">*</span>
                </label>
                <div class="tooltip-wrapper">
                  <i class="bi bi-info-circle info-icon" 
                     data-bs-toggle="tooltip" 
                     data-bs-placement="top" 
                     title="The International Mobile Equipment Identity (IMEI) is a unique 15-digit code that identifies your GPS device. It can be found on the device label, packaging, or by contacting the manufacturer."></i>
                </div>
              </div>
              
              <div class="input-wrapper" :class="{'is-invalid': errors.imei, 'is-valid': isImeiValid && device.imei.length > 0}">
                <input 
                  type="text" 
                  id="imei" 
                  v-model="device.imei" 
                  class="form-control" 
                  :class="{
                    'is-invalid': errors.imei,
                    'is-valid': isImeiValid && device.imei.length > 0
                  }"
                  :disabled="isEditMode && isImeiValid"
                  aria-describedby="imeiHelp imeiError imeiFormat"
                  maxlength="20"
                  pattern="^[0-9]{8,20}$"
                  @input="formatImei"
                  @focus="imeiFocused = true"
                  @blur="imeiFocused = false"
                  placeholder="Enter IMEI number (e.g., 123456789012345)"
                >
                <div id="imeiFormat" class="format-badge" :class="{'active': device.imei.length > 0}">
                  <i class="bi bi-check-circle-fill" v-if="isImeiValid"></i>
                  <i class="bi bi-exclamation-circle-fill" v-else-if="device.imei.length > 0"></i>
                  {{ device.imei.length }} digits
                </div>
              </div>
              
              <div class="input-feedback-area">
                <div v-if="errors.imei" id="imeiError" class="invalid-feedback d-block" role="alert">
                  <i class="bi bi-exclamation-triangle-fill me-1"></i> {{ errors.imei }}
                </div>
                <div v-else-if="isImeiValid && device.imei.length > 0" class="valid-feedback d-block">
                  <i class="bi bi-check-circle-fill me-1"></i> Valid IMEI format
                </div>
                <div id="imeiHelp" class="form-text mt-1">
                  <!-- Format guide remains visible at all times -->
                  <div class="format-guide">
                    <i class="bi bi-123 me-1"></i> <strong>Format:</strong> 8-20 digits (numbers only)
                  </div>
                  <div>
                    <i class="bi bi-lightbulb me-1"></i> <strong>Where to find it:</strong> On the device label, packaging, or by contacting the manufacturer
                  </div>
                  <div class="mt-1 text-muted">
                    <i class="bi bi-info-circle me-1"></i> The IMEI is the unique identifier for your GPS tracker and is required for registration
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Internal Device ID field - Optional and less prominent -->
            <div class="form-group" v-if="isAdvancedMode">
              <div class="label-with-tooltip">
                <label for="deviceId" class="form-label">
                  Internal Device ID
                </label>
                <div class="tooltip-wrapper">
                  <i class="bi bi-info-circle info-icon" 
                     data-bs-toggle="tooltip" 
                     data-bs-placement="top" 
                     title="Optional internal identifier. In most cases, you should leave this empty and the system will generate one automatically."></i>
                </div>
              </div>
              
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="deviceId" 
                  v-model="device.device_id" 
                  class="form-control" 
                  :disabled="isEditMode"
                  placeholder="Leave empty to auto-generate"
                >
              </div>
              <small class="text-muted">
                For advanced users only. The system will generate this value automatically if left empty.
              </small>
            </div>

            <div class="form-group">
              <label for="deviceName" class="form-label">Device Name</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="deviceName" 
                  v-model="device.name" 
                  class="form-control" 
                  placeholder="Enter a name for this device"
                >
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="deviceType" class="form-label">Device Type</label>
              <div class="input-wrapper">
                <select id="deviceType" v-model="device.device_type" class="form-select">
                  <option value="" disabled selected>Select a device type</option>
                  <option value="GPS Collar">GPS Collar</option>
                  <option value="Smart Tag">Smart Tag</option>
                  <option value="Tracker">Tracker</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="serialNumber" class="form-label">Serial Number</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="serialNumber" 
                  v-model="device.serial_number" 
                  class="form-control"
                  placeholder="Enter serial number (if available)"
                >
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="firmwareVersion" class="form-label">Firmware Version</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="firmwareVersion" 
                  v-model="device.firmware_version" 
                  class="form-control"
                  placeholder="Enter firmware version (if known)"
                >
              </div>
            </div>
            
            <div class="form-group">
              <label for="batteryLevel" class="form-label">Battery Level (%)</label>
              <div class="input-wrapper">
                <input 
                  type="number" 
                  id="batteryLevel" 
                  v-model="device.battery_level" 
                  class="form-control"
                  min="0"
                  max="100"
                  step="1"
                  placeholder="Current battery level"
                >
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <div class="form-check form-switch">
              <input 
                class="form-check-input" 
                type="checkbox" 
                id="isActive"
                v-model="device.is_active"
              >
              <label class="form-check-label" for="isActive">Device is active</label>
            </div>
          </div>
          
          <div class="form-group advanced-settings">
            <button type="button" class="btn btn-sm btn-outline-secondary" @click="toggleAdvancedMode">
              <i class="bi" :class="isAdvancedMode ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
              {{ isAdvancedMode ? 'Hide Advanced Settings' : 'Show Advanced Settings' }}
            </button>
          </div>
          
          <div class="form-group">
            <label for="petId" class="form-label">Assign to Pet</label>
            <div class="input-wrapper">
              <select id="petId" v-model="device.pet_id" class="form-select">
                <option value="">Not assigned</option>
                <option v-for="pet in pets" :key="pet.id" :value="pet.id">
                  {{ pet.name }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="$router.go(-1)">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? 'Saving...' : (isEditMode ? 'Update Device' : 'Add Device') }}
            </button>
          </div>
        </form>
      </card-component>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';
import { devicesAPI, petsAPI } from '../services/api.js';
import * as bootstrap from 'bootstrap';

export default {
  name: 'DeviceForm',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      device: {
        device_id: '',
        name: '',
        device_type: '',
        serial_number: '',
        imei: '',
        firmware_version: '',
        is_active: true,
        pet_id: ''
      },
      pets: [],
      isLoading: false,
      errors: {},
      globalError: null,
      requiredFields: ['imei', 'name'],
      deviceIdFocused: false,
      imeiFocused: false,
      isAdvancedMode: false,
      deviceIdVisualization: [
        ['P', 'T'], 
        ['1', '2'], 
        ['3', '4'], 
        ['5', '6'], 
        ['7', '8']
      ]
    }
  },
  computed: {
    isEditMode() {
      return this.$route.path.includes('/edit');
    },
    deviceId() {
      return this.$route.params.id;
    },
    isDeviceIdValid() {
      if (!this.device.device_id) return true; // Optional now, so empty is valid
      
      const deviceIdPattern = /^[A-Za-z0-9]{10}$/;
      return deviceIdPattern.test(this.device.device_id);
    },
    isImeiValid() {
      if (!this.device.imei) return false;
      
      // IMEI should be at least 8 digits, typically 15 digits
      const imeiPattern = /^[0-9]{8,20}$/;
      return imeiPattern.test(this.device.imei);
    }
  },
  mounted() {
    this.fetchPets();
    if (this.isEditMode) {
      this.fetchDeviceDetails();
    }
    
    // Initialize Bootstrap tooltips after component is mounted
    setTimeout(() => {
      const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
      tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
      });
    }, 100);
  },
  methods: {
    async fetchPets() {
      try {
        const response = await petsAPI.getAll();
        this.pets = response.data;
      } catch (error) {
        console.error('Error fetching pets:', error);
        this.globalError = 'Failed to load pets list. Please try again.';
      }
    },
    
    async fetchDeviceDetails() {
      try {
        this.isLoading = true;
        console.log('Fetching device details for ID:', this.deviceId);
        const response = await devicesAPI.getById(this.deviceId);
        
        // Log the response to help debugging
        console.log('Device details received:', response.data);
        
        // Handle pet_id as a special case (convert null to empty string for the form)
        const deviceData = { ...response.data };
        if (deviceData.pet_id === null) {
          deviceData.pet_id = '';
        }
        
        // Update the device data
        this.device = deviceData;
        this.isLoading = false;
      } catch (error) {
        console.error('Error fetching device details:', error);
        this.isLoading = false;
        this.globalError = 'Failed to load device details. Please try again.';
        
        // Show more detailed error information in the console
        if (error.response) {
          console.error('Error response:', error.response.status, error.response.data);
        }
        
        // Redirect back to devices list if the device is not found
        if (error.response && error.response.status === 404) {
          this.$router.push('/devices');
        }
      }
    },
    
    async saveDevice() {
      this.isLoading = true;
      this.errors = {};
      this.globalError = null;
      
      try {
        // Validate form fields
        this.validateForm();
        
        // If no validation errors, proceed with API call
        if (Object.keys(this.errors).length === 0) {
          console.log('Saving device:', this.device);
          
          // Use devicesAPI service to create or update the device
          if (this.isEditMode) {
            const response = await devicesAPI.update(this.deviceId, this.device);
            console.log('Device updated successfully:', response.data);
          } else {
            const response = await devicesAPI.create(this.device);
            console.log('Device created successfully:', response.data);
          }
          
          // Navigate back to devices list on success
          this.$router.push('/devices');
        } else {
          // If there are validation errors, stop loading state
          this.isLoading = false;
        }
      } catch (error) {
        console.error('Error saving device:', error);
        this.isLoading = false;
        
        // Add global error if server returns error
        if (error.response) {
          this.globalError = error.response.data.error || 'Failed to save device. Please try again.';
          
          // If the server returns field-specific errors, update the errors object
          if (error.response.data.errors) {
            this.errors = { ...this.errors, ...error.response.data.errors };
          }
        } else {
          this.globalError = 'Network error. Please check your connection and try again.';
        }
      }
    },
    
    validateForm() {
      // Reset errors before validation
      this.errors = {};
      this.globalError = null;
      
      // Validate required fields
      this.requiredFields.forEach(field => {
        if (!this.device[field] || this.device[field].trim() === '') {
          this.errors[field] = `${field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ')} is required`;
        }
      });
      
      // Validate device ID format if provided (optional field)
      if (this.device.device_id && !this.isEditMode) {
        const deviceIdPattern = /^[A-Za-z0-9]{10}$/;
        if (!deviceIdPattern.test(this.device.device_id)) {
          this.errors.device_id = "Device ID must be exactly 10 alphanumeric characters";
        }
      }
      
      // Validate IMEI format (required field)
      if (this.device.imei && !this.isImeiValid) {
        this.errors.imei = "IMEI must contain 8-20 digits (numbers only)";
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    formatDeviceId() {
      // Only allow alphanumeric characters (letters and numbers)
      if (this.device.device_id) {
        this.device.device_id = this.device.device_id.replace(/[^A-Za-z0-9]/g, '');
        
        // Limit to 10 characters
        if (this.device.device_id.length > 10) {
          this.device.device_id = this.device.device_id.substring(0, 10);
        }
        
        // Automatically convert to uppercase for better readability
        this.device.device_id = this.device.device_id.toUpperCase();
      }
    },
    
    // Get character at specified position in device ID
    getDeviceIdCharAt(index) {
      if (!this.device.device_id || index >= this.device.device_id.length) {
        return '';
      }
      return this.device.device_id.charAt(index);
    },
    
    // Get current cursor position to highlight in the visual guide
    getCurrentCharPosition() {
      return this.device.device_id ? this.device.device_id.length : 0;
    },
    
    // Format IMEI input to only allow digits
    formatImei() {
      if (this.device.imei) {
        // Only allow numeric characters
        this.device.imei = this.device.imei.replace(/[^0-9]/g, '');
        
        // Limit to 20 characters
        if (this.device.imei.length > 20) {
          this.device.imei = this.device.imei.substring(0, 20);
        }
      }
    },
    
    // Toggle advanced mode to show/hide internal device ID field
    toggleAdvancedMode() {
      this.isAdvancedMode = !this.isAdvancedMode;
    }
  }
}
</script>

<style scoped>
.form-container {
  max-width: 900px;
  margin: 0 auto;
}

.form-group {
  margin-bottom: 24px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
}

.form-check {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.form-check-input {
  width: 48px;
  height: 24px;
  margin-right: 12px;
  cursor: pointer;
}

.text-muted {
  color: var(--text-lighter);
  font-size: 13px;
  margin-top: 4px;
  display: block;
}

.btn-secondary {
  background-color: var(--background);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background-color: var(--border);
}

/* Validation styling */
.is-invalid {
  border-color: #dc3545 !important;
}

.form-control.is-invalid,
.form-select.is-invalid {
  border-color: #dc3545 !important;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12' width='12' height='12' fill='none' stroke='%23dc3545'%3e%3ccircle cx='6' cy='6' r='4.5'/%3e%3cpath stroke-linejoin='round' d='M5.8 3.6h.4L6 6.5z'/%3e%3ccircle cx='6' cy='8.2' r='.6' fill='%23dc3545' stroke='none'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 16px;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Required field indicator */
label .text-danger {
  font-weight: bold;
}

/* Device ID format styling */
.input-wrapper {
  position: relative;
}

/* Label and tooltip */
.label-with-tooltip {
  display: flex;
  align-items: center;
  margin-bottom: 6px;
}

.tooltip-wrapper {
  margin-left: 8px;
  display: flex;
  align-items: center;
}

.info-icon {
  color: var(--primary);
  font-size: 16px;
  cursor: help;
}

/* Format badge */
.format-badge {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background-color: var(--primary-light);
  color: var(--text);
  padding: 2px 8px;
  border-radius: 16px;
  font-size: 12px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.format-badge.active {
  opacity: 1;
}

/* Visual character guide */
.device-id-visual-guide {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  display: flex;
  gap: 4px;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.device-id-visual-guide.focused {
  opacity: 1;
}

.character-group {
  display: flex;
  background-color: var(--background-lighter);
  border-radius: 4px;
  overflow: hidden;
}

.character-group span {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: monospace;
  font-size: 14px;
  color: var(--text-lighter);
  border-right: 1px solid var(--border);
  background-color: var(--background-light);
}

.character-group span:last-child {
  border-right: none;
}

.character-group span.filled {
  background-color: var(--primary-light);
  color: var(--primary-dark);
  font-weight: bold;
}

.character-group span.current {
  box-shadow: inset 0 0 0 2px var(--primary);
}

/* Feedback area */
.input-feedback-area {
  margin-top: 32px;
}

.form-text {
  color: var(--text-lighter);
  font-size: 14px;
}

.format-guide {
  display: flex;
  align-items: center;
  margin-bottom: 4px;
}

/* Valid feedback */
.valid-feedback {
  color: #198754;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
}

.valid-feedback i, 
.invalid-feedback i {
  margin-right: 4px;
}

/* Code formatting */
code {
  background-color: var(--background-lighter);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
  color: var(--primary);
}

/* Advanced settings styling */
.advanced-settings {
  margin: 1rem 0;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  text-align: center;
}

.btn-outline-secondary {
  border-color: var(--border);
  color: var(--text);
  font-size: 0.9rem;
  padding: 0.25rem 0.75rem;
}

.btn-outline-secondary:hover {
  background-color: var(--background-lighter);
  color: var(--primary);
}

.btn-outline-secondary i {
  margin-right: 0.25rem;
}
</style>
