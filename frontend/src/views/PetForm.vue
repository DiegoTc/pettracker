<template>
  <div class="pet-form-page">
    <div class="d-flex align-items-center mb-4">
      <router-link to="/pets" class="btn btn-outline-secondary me-3">
        <i class="bi bi-arrow-left"></i> Back
      </router-link>
      <h2 class="mb-0">{{ isEditMode ? 'Edit Pet' : 'Add New Pet' }}</h2>
    </div>

    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">{{ isEditMode ? 'Loading pet...' : 'Preparing form...' }}</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      {{ error }}
    </div>

    <form v-else @submit.prevent="submitForm" class="pet-form">
      <div class="card">
        <div class="card-body">
          <div class="row g-3">
            <!-- Pet Name -->
            <div class="col-md-6">
              <label for="petName" class="form-label">Pet Name</label>
              <input 
                type="text" 
                class="form-control" 
                id="petName" 
                v-model="form.name"
                placeholder="Enter pet's name"
                required
              >
            </div>

            <!-- Pet Type -->
            <div class="col-md-6">
              <label for="petType" class="form-label">Pet Type</label>
              <select 
                class="form-select" 
                id="petType" 
                v-model="form.pet_type" 
                required
              >
                <option value="" disabled>Select pet type</option>
                <option v-for="type in petTypes" :key="type" :value="type">
                  {{ type }}
                </option>
              </select>
            </div>

            <!-- Breed -->
            <div class="col-md-6">
              <label for="breed" class="form-label">Breed</label>
              <input 
                type="text" 
                class="form-control" 
                id="breed" 
                v-model="form.breed"
                placeholder="Enter breed (optional)"
              >
            </div>

            <!-- Color -->
            <div class="col-md-6">
              <label for="color" class="form-label">Color</label>
              <input 
                type="text" 
                class="form-control" 
                id="color" 
                v-model="form.color"
                placeholder="Enter color (optional)"
              >
            </div>

            <!-- Birthdate -->
            <div class="col-md-6">
              <label for="birthdate" class="form-label">Birthdate</label>
              <input 
                type="date" 
                class="form-control" 
                id="birthdate" 
                v-model="form.birthdate"
              >
            </div>

            <!-- Weight -->
            <div class="col-md-6">
              <label for="weight" class="form-label">Weight (kg)</label>
              <input 
                type="number" 
                class="form-control" 
                id="weight" 
                v-model="form.weight"
                step="0.1"
                min="0"
                placeholder="Enter weight (optional)"
              >
            </div>

            <!-- Image URL -->
            <div class="col-12">
              <label for="imageUrl" class="form-label">Image URL</label>
              <input 
                type="url" 
                class="form-control" 
                id="imageUrl" 
                v-model="form.image_url"
                placeholder="https://example.com/pet-image.jpg (optional)"
              >
              <div class="form-text">Add a link to your pet's photo</div>
            </div>

            <!-- Description -->
            <div class="col-12">
              <label for="description" class="form-label">Description</label>
              <textarea 
                class="form-control" 
                id="description" 
                v-model="form.description"
                rows="3"
                placeholder="Tell us about your pet (optional)"
              ></textarea>
            </div>
          </div>
        </div>

        <div class="card-footer bg-white">
          <div class="d-flex justify-content-between">
            <router-link to="/pets" class="btn btn-outline-secondary">
              Cancel
            </router-link>
            <button type="submit" class="btn btn-primary" :disabled="submitting">
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
              {{ isEditMode ? 'Update Pet' : 'Add Pet' }}
            </button>
          </div>
        </div>
      </div>
    </form>

    <!-- Pet Preview (if editing and has image) -->
    <div v-if="isEditMode && form.image_url" class="card mt-4">
      <div class="card-header">
        <h5 class="mb-0">Pet Image Preview</h5>
      </div>
      <div class="card-body text-center">
        <img :src="form.image_url" alt="Pet Image" class="img-fluid" style="max-height: 300px;">
      </div>
    </div>
  </div>
</template>

<script>
import { petsAPI } from '../services/api';

export default {
  name: 'PetForm',
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
      petTypes: ['Dog', 'Cat', 'Bird', 'Other'],
      form: {
        name: '',
        pet_type: '',
        breed: '',
        color: '',
        birthdate: '',
        weight: '',
        image_url: '',
        description: ''
      }
    };
  },
  async created() {
    this.isEditMode = !!this.id;
    
    // If editing, fetch the pet data
    if (this.isEditMode) {
      try {
        const response = await petsAPI.getById(this.id);
        const pet = response.data;
        
        // Format the date from ISO to YYYY-MM-DD for the input field
        let birthdate = '';
        if (pet.birthdate) {
          const date = new Date(pet.birthdate);
          birthdate = date.toISOString().split('T')[0];
        }
        
        // Populate form with pet data
        this.form = {
          name: pet.name,
          pet_type: pet.pet_type,
          breed: pet.breed || '',
          color: pet.color || '',
          birthdate: birthdate,
          weight: pet.weight || '',
          image_url: pet.image_url || '',
          description: pet.description || ''
        };
      } catch (error) {
        console.error('Error fetching pet:', error);
        this.error = error.response?.data?.message || 'Failed to load pet';
      }
    }
    
    this.loading = false;
  },
  methods: {
    async submitForm() {
      this.submitting = true;
      this.error = null;
      
      try {
        // Create a copy of the form data to send to the API
        const petData = { ...this.form };
        
        // If weight is empty string, set to null
        if (petData.weight === '') {
          petData.weight = null;
        }
        
        if (this.isEditMode) {
          // Update existing pet
          await petsAPI.update(this.id, petData);
        } else {
          // Create new pet
          await petsAPI.create(petData);
        }
        
        // Redirect back to pets list
        this.$router.push('/pets');
      } catch (error) {
        console.error('Error saving pet:', error);
        this.error = error.response?.data?.message || 'Failed to save pet';
        window.scrollTo(0, 0); // Scroll to the top to show the error
      } finally {
        this.submitting = false;
      }
    }
  }
};
</script>

<style scoped>
.pet-form-page {
  margin-bottom: 50px;
}
</style>
