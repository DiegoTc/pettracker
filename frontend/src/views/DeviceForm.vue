<template>
  <div class="device-form-page">
    <div class="d-flex align-items-center mb-4">
      <router-link to="/devices" class="btn btn-outline-secondary me-3">
        <i class="bi bi-arrow-left"></i> Back
      </router-link>
      <h2 class="mb-0">{{ isEditMode ? 'Edit Device' : 'Register New Device' }}</h2>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">{{ isEditMode ? 'Loading device...' : 'Preparing form...' }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <form v-else @submit.prevent="submitForm" class="device-form">
      <div class="card">
        <div class="card-body">
          <div class="row g-3">
            <!-- Device Name -->
            <div class="col-md-6">
              <label for="deviceName" class="form-label">Device Name</label>
              <input 
                type="text" 
                class="form-control" 
                id="deviceName" 
                v-model="form.name"
                placeholder="My Pet Tracker"
                required
              >
              <div class="form-text">Give your device a recognizable name</div>
            </div>

            <!-- Device Type -->
            <div class="col-md-6">
              <label for="deviceType" class="form-label">Device Type</label>
              <input 
                type="text" 
                class="form-control" 
                id="deviceType" 
                v-model="form.device_type"
                placeholder="GPS Collar, Smart Tag, etc."
              >
            </div>

            <!-- Serial Number -->
            <div class="col-md-6">
              <label for="serialNumber" class="form-label">Serial Number</label>
              <input 
                type="text" 
                class="form-control" 
                id="serialNumber" 
                v-model="form.serial_number"
                placeholder="S/N from the device"
              >
              <div class="form-text">Usually found on the device or packaging</div>
            </div>

            <!-- IMEI Number -->
            <div class="col-md-6">
              <label for="imei" class="form-label">IMEI Number</label>
              <input 
                type="text" 
                class="form-control" 
                id="imei" 
                v-model="form.imei"
                placeholder="15-digit IMEI number"
                pattern="[0-9]{15}"
              >
              <div class="form-text">15-digit number unique to cellular devices</div>
            </div>

            <!-- Assign to Pet -->
            <div class="col-12">
              <label for="petId" class="form-label">Assign to Pet</label>
              <select 
                class="form-select" 
                id="petId" 
                v-model="form.pet_id"
              >
                <option value="">-- Not Assigned --</option>
                <option v-for="pet in pets" :key="pet.id" :value="pet.id">
                  {{ pet.name }} ({{ pet.pet_type }})
                </option>
              </select>
              <div class="form-text">Connect this device to one of your pets</div>
            </div>

            <!-- Device Status -->
            <div class="col-12">
              <div class="form-check form-switch">
                <input 
                  class="form-check-input" 
                  type="checkbox" 
                  id="isActive" 
                  v-model="form.is_active"
                >
                <label class="form-check-label" for="isActive">
                  Device is active and tracking
                </label>
              </div>
            </div>
          </div>
        </div>

        <div class="card-footer bg-white">
          <div class="d-flex justify-content-between">
            <router-link to="/devices" class="btn btn-outline-secondary">
              Cancel
            </router-link>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ isEditMode ? 'Update Device' : 'Register Device' }}
            </button>
          </div>
        </div>
      </div>
    </form>

    <!-- Device ID Information Card (when editing) -->
    <div v-if="isEditMode && device" class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Device Information</h5>
      </div>
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-4">
            <small class="text-muted">Device ID:</small>
            <div class="font-monospace">{{ device.device_id }}</div>
          </div>
          <div class="col-md-4" v-if="device.created_at">
            <small class="text-muted">Registered:</small>
            <div>{{ formatDate(device.created_at) }}</div>
          </div>
          <div class="col-md-4" v-if="device.last_ping">
            <small class="text-muted">Last Connection:</small>
            <div>{{ formatDate(device.last_ping) }}</div>
          </div>
        </div>

        <div v-if="device.battery_level" class="mb-3">
          <small class="text-muted">Battery Level:</small>
          <div class="progress">
            <div 
              class="progress-bar" 
              :class="getBatteryClass(device.battery_level)" 
              :style="{ width: `${device.battery_level}%` }" 
              role="progressbar"
              :aria-valuenow="device.battery_level" 
              aria-valuemin="0" 
              aria-valuemax="100"
            >
              {{ device.battery_level }}%
            </div>
          </div>
        </div>

        <div class="alert alert-info" v-if="device.firmware_version">
          <i class="bi bi-info-circle-fill me-2"></i>
          Current firmware version: <strong>{{ device.firmware_version }}</strong>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { devicesAPI, petsAPI } from '../services/api';

export default {
  name: 'DeviceForm',
  props: {
    id: {
      type: [String, Number],
      required: false
    }
  },
  data() {
    return {
      isEditMode: false,
      loading: true,
      submitting: false,
      error: null,
      device: null,
      pets: [],
      form: {
        name: '',
        device_type: '',
        serial_number: '',
        imei: '',
        pet_id: '',
        is_active: true
      }
    };
  },
  async created() {
    this.isEditMode = !!this.id;
    
    // Fetch pets to populate the dropdown
    try {
      const response = await petsAPI.getAll();
      this.pets = response.data;
    } catch (error) {
      console.error('Error fetching pets:', error);
    }
    
    // If editing, fetch the device data
    if (this.isEditMode) {
      try {
        const response = await devicesAPI.getById(this.id);
        this.device = response.data;
        
        // Populate form with device data
        this.form = {
          name: this.device.name,
          device_type: this.device.device_type,
          serial_number: this.device.serial_number,
          imei: this.device.imei,
          pet_id: this.device.pet_id || '',
          is_active: this.device.is_active
        };
      } catch (error) {
        console.error('Error fetching device:', error);
        this.error = error.response?.data?.message || 'Failed to load device';
      }
    }
    
    this.loading = false;
  },
  methods: {
    async submitForm() {
      this.submitting = true;
      this.error = null;
      
      try {
        if (this.isEditMode) {
          // Update existing device
          await devicesAPI.update(this.id, this.form);
          this.$router.push('/devices');
        } else {
          // Create new device
          await devicesAPI.create(this.form);
          this.$router.push('/devices');
        }
      } catch (error) {
        console.error('Error saving device:', error);
        this.error = error.response?.data?.message || 'Failed to save device';
        window.scrollTo(0, 0); // Scroll to the top to show the error
      } finally {
        this.submitting = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return null;
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('default', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    },
    getBatteryClass(level) {
      if (level <= 20) return 'bg-danger';
      if (level <= 40) return 'bg-warning';
      return 'bg-success';
    }
  }
};
</script>

<style scoped>
.device-form-page {
  margin-bottom: 50px;
}
</style>
