<template>
  <div class="device-form">
    <h2>{{ isEditMode ? 'Edit Device' : 'Register New Device' }}</h2>
    
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading device data...</p>
    </div>
    
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>
    
    <form v-else @submit.prevent="saveDevice" class="mt-4">
      <div class="mb-3">
        <label for="deviceName" class="form-label">Device Name</label>
        <input 
          type="text" 
          class="form-control" 
          id="deviceName" 
          v-model="device.name" 
          :class="{ 'is-invalid': errors.name }"
        >
        <div class="invalid-feedback" v-if="errors.name">{{ errors.name }}</div>
        <small class="form-text text-muted">A friendly name to identify your device</small>
      </div>
      
      <div class="mb-3">
        <label for="deviceType" class="form-label">Device Type</label>
        <select 
          class="form-select" 
          id="deviceType" 
          v-model="device.device_type" 
          :class="{ 'is-invalid': errors.device_type }"
        >
          <option value="">Select a device type</option>
          <option value="GPS Tracker">GPS Tracker</option>
          <option value="Collar">Smart Collar</option>
          <option value="Tag">Smart Tag</option>
          <option value="Other">Other</option>
        </select>
        <div class="invalid-feedback" v-if="errors.device_type">{{ errors.device_type }}</div>
      </div>
      
      <div class="mb-3">
        <label for="serialNumber" class="form-label">Serial Number</label>
        <input 
          type="text" 
          class="form-control" 
          id="serialNumber" 
          v-model="device.serial_number"
          :class="{ 'is-invalid': errors.serial_number }"
          :disabled="isEditMode"
        >
        <div class="invalid-feedback" v-if="errors.serial_number">{{ errors.serial_number }}</div>
        <small class="form-text text-muted">The serial number printed on your device</small>
      </div>
      
      <div class="mb-3">
        <label for="imei" class="form-label">IMEI Number</label>
        <input 
          type="text" 
          class="form-control" 
          id="imei" 
          v-model="device.imei"
          :class="{ 'is-invalid': errors.imei }"
          :disabled="isEditMode"
        >
        <div class="invalid-feedback" v-if="errors.imei">{{ errors.imei }}</div>
        <small class="form-text text-muted">The IMEI number of your tracking device (usually 15 digits)</small>
      </div>
      
      <div class="mb-3">
        <label for="firmwareVersion" class="form-label">Firmware Version</label>
        <input 
          type="text" 
          class="form-control" 
          id="firmwareVersion" 
          v-model="device.firmware_version"
          :class="{ 'is-invalid': errors.firmware_version }"
        >
        <div class="invalid-feedback" v-if="errors.firmware_version">{{ errors.firmware_version }}</div>
      </div>
      
      <div class="form-check form-switch mb-3">
        <input 
          class="form-check-input" 
          type="checkbox" 
          id="isActive" 
          v-model="device.is_active"
        >
        <label class="form-check-label" for="isActive">Device Active</label>
      </div>
      
      <div class="mb-3" v-if="isEditMode && pets.length > 0">
        <label for="petId" class="form-label">Assign to Pet</label>
        <select 
          class="form-select" 
          id="petId" 
          v-model="assignedPetId"
        >
          <option value="">Not assigned</option>
          <option v-for="pet in pets" :key="pet.id" :value="pet.id">{{ pet.name }}</option>
        </select>
        <small class="form-text text-muted">Select a pet to assign this device to</small>
      </div>
      
      <div class="alert alert-info" v-if="isEditMode">
        <h5>Device Information</h5>
        <p class="mb-1"><strong>Device ID:</strong> {{ device.device_id }}</p>
        <p class="mb-1" v-if="device.last_ping"><strong>Last Ping:</strong> {{ formatDateTime(device.last_ping) }}</p>
        <p class="mb-1" v-if="device.battery_level"><strong>Battery Level:</strong> {{ Math.round(device.battery_level) }}%</p>
        <p class="mb-0"><strong>Created:</strong> {{ formatDateTime(device.created_at) }}</p>
      </div>
      
      <div class="d-flex justify-content-between mt-4">
        <router-link to="/devices" class="btn btn-secondary">
          Cancel
        </router-link>
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
          {{ submitting ? 'Saving...' : (isEditMode ? 'Update Device' : 'Register Device') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DeviceForm',
  props: {
    id: {
      type: String,
      required: false
    }
  },
  data() {
    return {
      device: {
        name: '',
        device_type: '',
        serial_number: '',
        imei: '',
        firmware_version: '',
        is_active: true
      },
      pets: [],
      assignedPetId: '',
      loading: false,
      submitting: false,
      error: null,
      errors: {}
    };
  },
  computed: {
    isEditMode() {
      return !!this.id;
    }
  },
  async created() {
    await this.fetchPets();
    if (this.isEditMode) {
      await this.fetchDevice();
    }
  },
  methods: {
    async fetchPets() {
      try {
        const response = await axios.get('/api/pets');
        this.pets = response.data;
      } catch (error) {
        console.error('Error fetching pets:', error);
      }
    },
    async fetchDevice() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get(`/api/devices/${this.id}`);
        this.device = response.data;
        
        // Set assigned pet if any
        if (this.device.pet_id) {
          this.assignedPetId = this.device.pet_id;
        }
      } catch (error) {
        console.error('Error fetching device:', error);
        this.error = error.response?.data?.message || 'Failed to load device data';
      } finally {
        this.loading = false;
      }
    },
    async saveDevice() {
      this.submitting = true;
      this.errors = {};
      
      try {
        let response;
        if (this.isEditMode) {
          // First update the device
          response = await axios.put(`/api/devices/${this.id}`, this.device);
          
          // Then handle pet assignment if needed
          if (this.assignedPetId) {
            await axios.post(`/api/devices/${this.id}/assign/${this.assignedPetId}`);
          } else if (this.device.pet_id) {
            // Unassign if previously assigned but now empty
            await axios.post(`/api/devices/${this.id}/unassign`);
          }
        } else {
          response = await axios.post('/api/devices', this.device);
        }
        
        // Navigate back to devices list
        this.$router.push('/devices');
      } catch (error) {
        console.error('Error saving device:', error);
        if (error.response?.status === 400 && error.response.data.errors) {
          // Validation errors
          this.errors = error.response.data.errors;
        } else {
          this.error = error.response?.data?.message || 'Failed to save device';
        }
      } finally {
        this.submitting = false;
      }
    },
    formatDateTime(dateTimeStr) {
      if (!dateTimeStr) return 'N/A';
      const date = new Date(dateTimeStr);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.device-form {
  max-width: 800px;
  margin: 0 auto 50px auto;
}
</style>
