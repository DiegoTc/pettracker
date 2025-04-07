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
      <h4 class="mt-3">No devices registered yet</h4>
      <p class="text-muted">Register your first tracking device to start monitoring your pets</p>
      <router-link to="/devices/new" class="btn btn-primary mt-2">
        Register New Device
      </router-link>
    </div>

    <div v-else>
      <div class="table-responsive">
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Device ID</th>
              <th>Type</th>
              <th>Status</th>
              <th>Battery</th>
              <th>Last Ping</th>
              <th>Assigned Pet</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" :key="device.id">
              <td>{{ device.name || 'Unnamed Device' }}</td>
              <td>
                <span class="badge bg-secondary">{{ device.device_id }}</span>
              </td>
              <td>{{ device.device_type || 'Unknown' }}</td>
              <td>
                <span 
                  class="badge" 
                  :class="device.is_active ? 'bg-success' : 'bg-danger'"
                >
                  {{ device.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <div class="progress" style="height: 20px; width: 100px;">
                  <div 
                    class="progress-bar" 
                    role="progressbar" 
                    :style="{ width: `${device.battery_level || 0}%` }"
                    :class="getBatteryColorClass(device.battery_level)"
                  >
                    {{ device.battery_level ? `${Math.round(device.battery_level)}%` : 'N/A' }}
                  </div>
                </div>
              </td>
              <td>
                <span v-if="device.last_ping">
                  {{ formatDate(device.last_ping) }}
                </span>
                <span v-else class="text-muted">Never</span>
              </td>
              <td>
                <span v-if="device.pet">
                  {{ device.pet.name }}
                </span>
                <span v-else>
                  <button 
                    class="btn btn-sm btn-outline-primary" 
                    @click="showAssignModal(device)"
                    :disabled="pets.length === 0"
                  >
                    Assign
                  </button>
                </span>
              </td>
              <td>
                <div class="btn-group">
                  <router-link :to="`/devices/${device.id}/edit`" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-pencil"></i>
                  </router-link>
                  <button class="btn btn-sm btn-outline-danger" @click="confirmDelete(device)">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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
            <p class="text-danger">This action cannot be undone and will delete all associated location data.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteDevice">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Assign to Pet Modal -->
    <div class="modal fade" id="assignModal" tabindex="-1" ref="assignModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Assign to Pet</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="deviceToAssign">
            <p>Select a pet to assign device <strong>{{ deviceToAssign.name || deviceToAssign.device_id }}</strong> to:</p>
            
            <div class="form-group">
              <select class="form-select" v-model="selectedPetId">
                <option disabled value="">Choose a pet</option>
                <option v-for="pet in pets" :key="pet.id" :value="pet.id">{{ pet.name }}</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="assignToPet"
              :disabled="!selectedPetId"
            >
              Assign
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Modal } from 'bootstrap';

export default {
  name: 'Devices',
  data() {
    return {
      devices: [],
      pets: [],
      loading: true,
      error: null,
      deviceToDelete: null,
      deviceToAssign: null,
      selectedPetId: '',
      deleteModal: null,
      assignModal: null
    };
  },
  async created() {
    await Promise.all([
      this.fetchDevices(),
      this.fetchPets()
    ]);
  },
  mounted() {
    // Initialize modals
    this.deleteModal = new Modal(this.$refs.deleteModal);
    this.assignModal = new Modal(this.$refs.assignModal);
  },
  methods: {
    async fetchDevices() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/devices');
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
        const response = await axios.get('/api/pets');
        this.pets = response.data;
      } catch (error) {
        console.error('Error fetching pets:', error);
      }
    },
    getBatteryColorClass(level) {
      if (!level) return 'bg-secondary';
      if (level < 20) return 'bg-danger';
      if (level < 50) return 'bg-warning';
      return 'bg-success';
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      const date = new Date(dateStr);
      // Check if date is today
      const today = new Date();
      if (date.toDateString() === today.toDateString()) {
        return 'Today ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
      // Check if date is yesterday
      const yesterday = new Date();
      yesterday.setDate(yesterday.getDate() - 1);
      if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
      // Otherwise show full date
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    confirmDelete(device) {
      this.deviceToDelete = device;
      this.deleteModal.show();
    },
    async deleteDevice() {
      if (!this.deviceToDelete) return;
      
      try {
        await axios.delete(`/api/devices/${this.deviceToDelete.id}`);
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
    showAssignModal(device) {
      this.deviceToAssign = device;
      this.selectedPetId = '';
      this.assignModal.show();
    },
    async assignToPet() {
      if (!this.deviceToAssign || !this.selectedPetId) return;
      
      try {
        await axios.post(`/api/devices/${this.deviceToAssign.id}/assign/${this.selectedPetId}`);
        // Update the device in the list
        const petName = this.pets.find(p => p.id === this.selectedPetId)?.name || '';
        
        // Refresh the devices list to get updated data
        await this.fetchDevices();
        
        this.assignModal.hide();
        // Show success message
        this.showAlert(`Device assigned to ${petName} successfully`, 'success');
      } catch (error) {
        console.error('Error assigning device:', error);
        this.showAlert(error.response?.data?.message || 'Failed to assign device', 'danger');
      } finally {
        this.deviceToAssign = null;
        this.selectedPetId = '';
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
