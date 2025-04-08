<template>
  <div class="devices-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Devices</h2>
      <router-link to="/devices/new" class="btn btn-primary">
        <i class="bi bi-plus-lg"></i> Register New Device
      </router-link>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your devices...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      Error loading devices: {{ error }}
    </div>

    <div v-else-if="devices.length === 0" class="text-center my-5">
      <i class="bi bi-cpu display-4 text-muted"></i>
      <h4 class="mt-3">No tracking devices registered</h4>
      <p class="text-muted">Register a new device to start tracking your pets</p>
      <router-link to="/devices/new" class="btn btn-primary mt-2">
        Register New Device
      </router-link>
    </div>

    <div v-else class="row">
      <div v-for="device in devices" :key="device.id" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">{{ device.name || 'Unnamed Device' }}</h5>
            <span v-if="device.is_active" class="badge bg-success">Active</span>
            <span v-else class="badge bg-secondary">Inactive</span>
          </div>
          <div class="card-body">
            <div class="mb-3">
              <small class="text-muted">Device ID:</small>
              <div class="font-monospace">{{ device.device_id }}</div>
            </div>
            
            <div class="mb-3" v-if="device.device_type">
              <small class="text-muted">Type:</small>
              <div>{{ device.device_type }}</div>
            </div>
            
            <div class="mb-3" v-if="device.serial_number">
              <small class="text-muted">Serial Number:</small>
              <div class="font-monospace">{{ device.serial_number }}</div>
            </div>
            
            <div class="mb-3" v-if="device.imei">
              <small class="text-muted">IMEI:</small>
              <div class="font-monospace">{{ device.imei }}</div>
            </div>
            
            <div class="mb-3">
              <small class="text-muted">Last Connection:</small>
              <div>{{ formatDate(device.last_ping) || 'Never' }}</div>
            </div>
            
            <div class="battery-indicator mb-3" v-if="device.battery_level">
              <small class="text-muted">Battery Level:</small>
              <div class="progress">
                <div 
                  class="progress-bar" 
                  :class="getBatteryClass(device.battery_level)"
                  :style="{ width: `${device.battery_level}%` }"
                  role="progressbar" 
                  :aria-valuenow="device.battery_level" 
                  aria-valuemin="0" 
                  aria-valuemax="100">
                  {{ device.battery_level }}%
                </div>
              </div>
            </div>
            
            <div v-if="device.pet_id">
              <small class="text-muted">Assigned to:</small>
              <div>
                <span class="badge bg-info">{{ getPetName(device.pet_id) }}</span>
              </div>
            </div>
            <div v-else>
              <small class="text-muted">Status:</small>
              <div>
                <span class="badge bg-warning text-dark">Not assigned to any pet</span>
              </div>
            </div>
          </div>
          <div class="card-footer bg-white">
            <div class="d-flex justify-content-between">
              <router-link :to="`/devices/${device.id}/edit`" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-pencil-square"></i> Edit
              </router-link>
              <button class="btn btn-outline-danger btn-sm" @click="confirmDelete(device)">
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Confirm Delete</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="deviceToDelete">
            <p>Are you sure you want to delete device <strong>{{ deviceToDelete.name || deviceToDelete.device_id }}</strong>?</p>
            <p class="text-danger">This action cannot be undone and will remove all location history for this device.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteDevice">Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Modal } from 'bootstrap';
import { devicesAPI, petsAPI } from '../services/api';

export default {
  name: 'Devices',
  data() {
    return {
      devices: [],
      pets: [],
      loading: true,
      error: null,
      deviceToDelete: null,
      deleteModal: null
    };
  },
  async created() {
    await Promise.all([
      this.fetchDevices(),
      this.fetchPets()
    ]);
  },
  mounted() {
    // Initialize the delete modal
    this.deleteModal = new Modal(this.$refs.deleteModal);
  },
  methods: {
    async fetchDevices() {
      this.loading = true;
      this.error = null;
      try {
        const response = await devicesAPI.getAll();
        this.devices = response.data;
      } catch (error) {
        console.error('Error fetching devices:', error);
        this.error = error.response?.data?.message || 'Failed to load devices';
      } finally {
        this.loading = false;
      }
    },
    async fetchPets() {
      try {
        const response = await petsAPI.getAll();
        this.pets = response.data;
      } catch (error) {
        console.error('Error fetching pets:', error);
      }
    },
    getPetName(petId) {
      const pet = this.pets.find(p => p.id === petId);
      return pet ? pet.name : 'Unknown Pet';
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
    },
    confirmDelete(device) {
      this.deviceToDelete = device;
      this.deleteModal.show();
    },
    async deleteDevice() {
      if (!this.deviceToDelete) return;
      
      try {
        await devicesAPI.delete(this.deviceToDelete.id);
        // Remove the device from the list
        this.devices = this.devices.filter(d => d.id !== this.deviceToDelete.id);
        this.deleteModal.hide();
        // Show success message
        this.showAlert('Device deleted successfully', 'success');
      } catch (error) {
        console.error('Error deleting device:', error);
        this.showAlert(error.response?.data?.message || 'Failed to delete device', 'danger');
      } finally {
        this.deviceToDelete = null;
      }
    },
    showAlert(message, type) {
      // This is a placeholder for an alert system
      // You might want to implement a toast notification system
      alert(message);
    }
  }
};
</script>

<style scoped>
.devices-page {
  margin-bottom: 50px;
}
</style>
