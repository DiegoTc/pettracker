<template>
  <div class="pets-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Pets</h2>
      <router-link to="/pets/new" class="btn btn-primary">
        <i class="bi bi-plus-lg"></i> Add New Pet
      </router-link>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading your pets...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      Error loading pets: {{ error }}
    </div>

    <div v-else-if="pets.length === 0" class="text-center my-5">
      <i class="bi bi-emoji-smile display-4 text-muted"></i>
      <h4 class="mt-3">No pets yet</h4>
      <p class="text-muted">Get started by adding your first pet</p>
      <router-link to="/pets/new" class="btn btn-primary mt-2">
        Add New Pet
      </router-link>
    </div>

    <div v-else class="row">
      <div v-for="pet in pets" :key="pet.id" class="col-md-4 mb-4">
        <div class="card h-100">
          <div class="card-img-top bg-light text-center py-3" style="height: 200px;">
            <img v-if="pet.image_url" :src="pet.image_url" alt="Pet Image" class="img-fluid h-100">
            <div v-else class="d-flex align-items-center justify-content-center h-100">
              <i class="bi bi-image text-muted" style="font-size: 4rem;"></i>
            </div>
          </div>
          <div class="card-body">
            <h5 class="card-title">{{ pet.name }}</h5>
            <p class="card-text">
              <span class="badge bg-info me-2">{{ pet.pet_type }}</span>
              <span v-if="pet.breed" class="badge bg-secondary">{{ pet.breed }}</span>
            </p>
            <p class="card-text" v-if="pet.description">{{ pet.description }}</p>
          </div>
          <div class="card-footer bg-white">
            <div class="d-flex justify-content-between">
              <router-link :to="'/pets/' + pet.id + '/edit'" class="btn btn-outline-primary btn-sm">
                <i class="bi bi-pencil-square"></i> Edit
              </router-link>
              <button class="btn btn-outline-danger btn-sm" @click="confirmDelete(pet)">
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
          <div class="modal-body" v-if="petToDelete">
            <p>Are you sure you want to delete <strong>{{ petToDelete.name }}</strong>?</p>
            <p class="text-danger">This action cannot be undone.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deletePet">Delete</button>
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
  name: 'Pets',
  data() {
    return {
      pets: [],
      loading: true,
      error: null,
      petToDelete: null,
      deleteModal: null
    };
  },
  async created() {
    await this.fetchPets();
  },
  mounted() {
    // Initialize the delete modal
    this.deleteModal = new Modal(this.$refs.deleteModal);
  },
  methods: {
    async fetchPets() {
      this.loading = true;
      this.error = null;
      try {
        const response = await axios.get('/api/pets');
        this.pets = response.data;
      } catch (error) {
        console.error('Error fetching pets:', error);
        this.error = error.response?.data?.message || 'Failed to load pets';
      } finally {
        this.loading = false;
      }
    },
    confirmDelete(pet) {
      this.petToDelete = pet;
      this.deleteModal.show();
    },
    async deletePet() {
      if (!this.petToDelete) return;
      
      try {
        await axios.delete(`/api/pets/${this.petToDelete.id}`);
        // Remove the pet from the list
        this.pets = this.pets.filter(p => p.id !== this.petToDelete.id);
        this.deleteModal.hide();
        // Show success message
        this.showAlert('Pet deleted successfully', 'success');
      } catch (error) {
        console.error('Error deleting pet:', error);
        this.showAlert(error.response?.data?.message || 'Failed to delete pet', 'danger');
      } finally {
        this.petToDelete = null;
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
.pets-page {
  margin-bottom: 50px;
}
</style>
