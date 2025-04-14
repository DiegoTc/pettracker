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
        <form @submit.prevent="saveDevice">
          <div class="form-row">
            <div class="form-group">
              <label for="deviceId" class="form-label">Device ID</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="deviceId" 
                  v-model="device.device_id" 
                  class="form-control" 
                  required 
                  :disabled="isEditMode"
                  placeholder="Enter device ID"
                >
              </div>
              <small class="text-muted" v-if="!isEditMode">
                Enter the unique ID provided with your GPS tracker
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
              <label for="imei" class="form-label">IMEI Number</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="imei" 
                  v-model="device.imei" 
                  class="form-control"
                  placeholder="Enter IMEI number (if available)"
                >
              </div>
            </div>
            
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
            <button type="submit" class="btn btn-primary">
              {{ isEditMode ? 'Update Device' : 'Add Device' }}
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
      isLoading: false
    }
  },
  computed: {
    isEditMode() {
      return this.$route.path.includes('/edit');
    },
    deviceId() {
      return this.$route.params.id;
    }
  },
  mounted() {
    this.fetchPets();
    if (this.isEditMode) {
      this.fetchDeviceDetails();
    }
  },
  methods: {
    fetchPets() {
      // Simulate API call
      setTimeout(() => {
        this.pets = [
          { id: 1, name: 'Buddy' },
          { id: 2, name: 'Max' },
          { id: 3, name: 'Luna' }
        ];
      }, 500);
      
      // Real API call will look like:
      /*
      fetch('/api/pets')
        .then(response => response.json())
        .then(data => {
          this.pets = data;
        })
        .catch(error => {
          console.error('Error fetching pets:', error);
        });
      */
    },
    fetchDeviceDetails() {
      // Simulate API call
      setTimeout(() => {
        this.device = {
          id: this.deviceId,
          device_id: 'ABC123',
          name: 'Buddy\'s Collar',
          device_type: 'GPS Collar',
          serial_number: 'SN123456789',
          imei: '123456789012345',
          firmware_version: '1.2.3',
          is_active: true,
          pet_id: 1
        };
      }, 500);
      
      // Real API call will look like:
      /*
      fetch(`/api/devices/${this.deviceId}`)
        .then(response => {
          if (!response.ok) throw new Error('Device not found');
          return response.json();
        })
        .then(data => {
          this.device = data;
        })
        .catch(error => {
          console.error('Error fetching device details:', error);
          this.$router.push('/devices');
        });
      */
    },
    saveDevice() {
      this.isLoading = true;
      
      console.log('Saving device:', this.device);
      
      // Simulate API save
      setTimeout(() => {
        this.isLoading = false;
        this.$router.push('/devices');
      }, 1000);
      
      // Real API call will look like:
      /*
      const url = this.isEditMode ? `/api/devices/${this.deviceId}` : '/api/devices';
      const method = this.isEditMode ? 'PUT' : 'POST';
      
      fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(this.device)
      })
        .then(response => {
          if (!response.ok) throw new Error('Failed to save device');
          return response.json();
        })
        .then(data => {
          this.$router.push('/devices');
        })
        .catch(error => {
          console.error('Error saving device:', error);
          this.isLoading = false;
        });
      */
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
</style>
