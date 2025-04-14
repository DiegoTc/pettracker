<template>
  <app-layout>
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex align-items-center mb-3">
          <i class="bi bi-pencil-square text-primary me-2"></i>
          <h5 class="card-title mb-0">Pet Information</h5>
        </div>

        <!-- Global Error Message -->
        <div v-if="globalError" class="alert alert-danger mb-3">
          {{ globalError }}
        </div>
        
        <form @submit.prevent="savePet">
          <div class="mb-3">
            <label for="petName" class="form-label">
              Pet Name <span class="text-danger">*</span>
            </label>
            <div class="input-wrapper" :class="{'is-invalid': errors.name}">
              <input 
                type="text" 
                id="petName" 
                v-model="pet.name" 
                class="form-control" 
                :class="{'is-invalid': errors.name}"
                placeholder="Enter pet name"
              >
            </div>
            <div v-if="errors.name" class="invalid-feedback d-block">
              {{ errors.name }}
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="petType" class="form-label">
                Pet Type <span class="text-danger">*</span>
              </label>
              <div class="input-wrapper" :class="{'is-invalid': errors.pet_type}">
                <select id="petType" v-model="pet.pet_type" class="form-select" :class="{'is-invalid': errors.pet_type}">
                  <option value="" disabled selected>Select a pet type</option>
                  <option value="Dog">Dog</option>
                  <option value="Cat">Cat</option>
                  <option value="Bird">Bird</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div v-if="errors.pet_type" class="invalid-feedback d-block">
                {{ errors.pet_type }}
              </div>
            </div>

            <div class="col-md-6 mb-3">
              <label for="breed" class="form-label">Breed</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="breed" 
                  v-model="pet.breed" 
                  class="form-control" 
                  placeholder="Enter breed"
                >
              </div>
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label for="color" class="form-label">Color</label>
              <div class="input-wrapper">
                <input 
                  type="text" 
                  id="color" 
                  v-model="pet.color" 
                  class="form-control" 
                  placeholder="Enter color"
                >
              </div>
            </div>

            <div class="col-md-6 mb-3">
              <label for="weight" class="form-label">Weight (kg)</label>
              <div class="input-wrapper" :class="{'is-invalid': errors.weight}">
                <input 
                  type="number" 
                  id="weight" 
                  v-model="pet.weight" 
                  class="form-control"
                  :class="{'is-invalid': errors.weight}"
                  step="0.1"
                  min="0"
                  placeholder="Enter weight"
                >
              </div>
              <div v-if="errors.weight" class="invalid-feedback d-block">
                {{ errors.weight }}
              </div>
            </div>
          </div>

          <div class="mb-3">
            <label for="birthdate" class="form-label">Birthdate</label>
            <div class="input-wrapper">
              <input 
                type="date" 
                id="birthdate" 
                v-model="pet.birthdate" 
                class="form-control"
              >
            </div>
          </div>

          <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <div class="input-wrapper">
              <textarea 
                id="description" 
                v-model="pet.description" 
                class="form-control" 
                rows="3"
                placeholder="Enter a description about your pet"
              ></textarea>
            </div>
          </div>

          <div class="mb-3">
            <label for="image" class="form-label">Pet Image</label>
            <div class="image-upload-container">
              <div class="image-preview rounded" v-if="pet.image_url">
                <img :src="pet.image_url" alt="Pet preview" class="img-fluid">
                <button type="button" class="btn-remove-image" @click="removeImage">
                  <i class="bi bi-x-circle-fill"></i>
                </button>
              </div>
              <div v-else class="image-upload rounded border d-flex justify-content-center align-items-center p-4" style="height: 180px; cursor: pointer;">
                <label for="image" class="upload-label text-center m-0">
                  <i class="bi bi-cloud-upload fs-3 d-block mb-2 text-primary"></i>
                  <span class="text-muted">Click to upload image</span>
                </label>
                <input 
                  type="file" 
                  id="image" 
                  @change="handleImageUpload"
                  accept="image/*"
                  hidden
                >
              </div>
            </div>
          </div>

          <div class="d-flex justify-content-end gap-2 mt-4">
            <button type="button" class="btn btn-light border" @click="$router.go(-1)">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary">
              {{ isEditMode ? 'Update Pet' : 'Add Pet' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </app-layout>
</template>

<script>
import AppLayout from '../components/layout/AppLayout.vue';
import CardComponent from '../components/common/CardComponent.vue';
import { petsAPI } from '../services/api.js';

export default {
  name: 'PetForm',
  components: {
    AppLayout,
    CardComponent
  },
  data() {
    return {
      pet: {
        name: '',
        pet_type: '',
        breed: '',
        color: '',
        weight: null,
        birthdate: '',
        description: '',
        image_url: null
      },
      isLoading: false,
      errors: {},
      globalError: null,
      requiredFields: ['name', 'pet_type']
    }
  },
  computed: {
    isEditMode() {
      return this.$route.path.includes('/edit');
    },
    petId() {
      return this.$route.params.id;
    }
  },
  mounted() {
    if (this.isEditMode) {
      this.fetchPetDetails();
    }
  },
  methods: {
    async fetchPetDetails() {
      try {
        this.isLoading = true;
        const response = await petsAPI.getById(this.petId);
        this.pet = response.data;
        this.isLoading = false;
      } catch (error) {
        console.error('Error fetching pet details:', error);
        this.isLoading = false;
        this.globalError = 'Failed to load pet details. Please try again.';
        // Redirect back to pets list if the pet is not found
        if (error.response && error.response.status === 404) {
          this.$router.push('/pets');
        }
      }
    },
    async savePet() {
      this.isLoading = true;
      this.errors = {};
      
      try {
        // Validate form fields
        this.validateForm();
        
        // If no validation errors, proceed with API call
        if (Object.keys(this.errors).length === 0) {
          console.log('Saving pet:', this.pet);
          
          // Use petsAPI service to create or update the pet
          if (this.isEditMode) {
            const response = await petsAPI.update(this.petId, this.pet);
            console.log('Pet updated successfully:', response.data);
          } else {
            const response = await petsAPI.create(this.pet);
            console.log('Pet created successfully:', response.data);
          }
          
          // Navigate back to pets list on success
          this.$router.push('/pets');
        } else {
          // If there are validation errors, stop loading state
          this.isLoading = false;
        }
      } catch (error) {
        console.error('Error saving pet:', error);
        this.isLoading = false;
        
        // Add global error if server returns error
        if (error.response) {
          this.globalError = error.response.data.error || 'Failed to save pet. Please try again.';
          
          // If the server returns field-specific errors, update the errors object
          if (error.response.data.errors) {
            this.errors = { ...this.errors, ...error.response.data.errors };
          }
        } else {
          this.globalError = 'Network error. Please check your connection and try again.';
        }
      }
    },
    handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      
      // For demo just use a local URL
      this.pet.image_url = URL.createObjectURL(file);
      
      // In a real implementation we would upload to server
    },
    removeImage() {
      this.pet.image_url = null;
    },
    
    validateForm() {
      // Reset errors before validation
      this.errors = {};
      this.globalError = null;
      
      // Validate required fields
      this.requiredFields.forEach(field => {
        if (!this.pet[field] || this.pet[field].trim() === '') {
          this.errors[field] = `${field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ')} is required`;
        }
      });
      
      // Validate weight if provided (must be positive)
      if (this.pet.weight !== null && this.pet.weight !== '' && this.pet.weight <= 0) {
        this.errors.weight = 'Weight must be greater than 0';
      }
      
      return Object.keys(this.errors).length === 0;
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

.image-upload-container {
  width: 100%;
  margin-top: 8px;
}

.image-upload {
  border: 2px dashed var(--border);
  border-radius: var(--radius);
  padding: a24px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: var(--background);
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  color: var(--text-light);
}

.upload-label i {
  font-size: 48px;
  margin-bottom: 8px;
}

.image-preview {
  position: relative;
  height: 200px;
  border-radius: var(--radius);
  overflow: hidden;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-image {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-remove-image:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

.btn-secondary {
  background-color: var(--background);
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background-color: var(--border);
}

/* Form specific styling */
.input-wrapper .form-select {
  appearance: auto;
  background-color: #ffffff;
  color: #333333;
  border: 1px solid #cccccc;
}

.input-wrapper .form-select:hover {
  border-color: #bbbbbb;
}

.input-wrapper .form-select:focus {
  border-color: var(--primary);
  outline: none;
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
</style>
