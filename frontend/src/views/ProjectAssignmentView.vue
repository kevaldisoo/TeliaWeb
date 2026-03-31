<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { api } from '@/api/index.js'
import { useEmployeeStore } from '@/stores/employee.js'

const store = useEmployeeStore()

const projects = ref([])
const notification = ref(null) // { type: 'success' | 'error', message: string }
const errors = ref({})        // field-level error messages, keyed by field name
const emailChecked = ref(false)

const emptyForm = () => ({
  full_name: '',
  email: '',
  experience_level: '',
  tech_stack: '',
  preferred_duration: '',
  additional_skills: '',
  availability_confirmed: false,
  project_ids: [],
})

const form = ref(emptyForm())

const isUpdate = computed(() => !!store.employee?.id)
const emailLocked = computed(() => isUpdate.value)

onMounted(async () => {
  projects.value = await api.getProjects().catch(() => [])
  await store.loadStoredEmployee()
  if (store.employee) fillForm(store.employee)
})

// ── Clear individual field errors as the user edits ──────────────────────────

watch(() => form.value.full_name,           () => clearError('full_name'))
watch(() => form.value.email,               () => clearError('email'))
watch(() => form.value.experience_level,    () => clearError('experience_level'))
watch(() => form.value.tech_stack,          () => clearError('tech_stack'))
watch(() => form.value.preferred_duration,  () => clearError('preferred_duration'))
watch(() => form.value.project_ids,         () => clearError('project_ids'), { deep: true })
watch(() => form.value.availability_confirmed, () => clearError('availability_confirmed'))

// ── Helpers ───────────────────────────────────────────────────────────────────

function fillForm(emp) {
  form.value.full_name              = emp.full_name
  form.value.email                  = emp.email
  form.value.experience_level       = emp.experience_level
  form.value.tech_stack             = emp.tech_stack
  form.value.preferred_duration     = emp.preferred_duration
  form.value.additional_skills      = emp.additional_skills ?? ''
  form.value.availability_confirmed = emp.availability_confirmed
  form.value.project_ids            = emp.projects.map((p) => p.id)
}

function clearError(field) {
  if (errors.value[field]) {
    const next = { ...errors.value }
    delete next[field]
    errors.value = next
  }
}

// ── Client-side validation ────────────────────────────────────────────────────

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate() {
  const e = {}

  if (!form.value.full_name.trim()) {
    e.full_name = 'Full name is required.'
  } else if (form.value.full_name.trim().length < 2) {
    e.full_name = 'Full name must be at least 2 characters.'
  }

  if (!form.value.email.trim()) {
    e.email = 'Email address is required.'
  } else if (!EMAIL_RE.test(form.value.email.trim())) {
    e.email = 'Please enter a valid email address (e.g. jane@company.com).'
  }

  if (!form.value.experience_level) {
    e.experience_level = 'Please select your experience level.'
  }

  if (!form.value.tech_stack) {
    e.tech_stack = 'Please select your primary technology stack.'
  }

  if (!form.value.preferred_duration) {
    e.preferred_duration = 'Please select a preferred project duration.'
  }

  if (form.value.project_ids.length === 0) {
    e.project_ids = 'Please select at least one project.'
  }

  if (!form.value.availability_confirmed) {
    e.availability_confirmed = 'Please confirm your availability before saving.'
  }

  errors.value = e
  return Object.keys(e).length === 0
}


async function handleEmailBlur() {
  const val = form.value.email.trim()

  // Real-time format check on blur
  if (val && !EMAIL_RE.test(val)) {
    errors.value = { ...errors.value, email: 'Please enter a valid email address (e.g. jane@company.com).' }
    return
  }

  if (emailChecked.value || !val || store.employee) return
  emailChecked.value = true

  const found = await store.lookupByEmail(val)
  if (found) {
    fillForm(found)
    errors.value = {}
    notify('success', 'Existing profile loaded — update your information and click Save Profile.')
  }
}

async function handleSubmit() {
  notification.value = null

  if (!validate()) {
    notify('error', 'Please fix the errors below before saving.')
    return
  }

  const wasUpdate = isUpdate.value

  try {
    await store.saveEmployee({ ...form.value })
    errors.value = {}
    notify(
      'success',
      wasUpdate ? 'Profile updated successfully!' : 'Profile registered successfully!',
    )
  } catch (e) {
    // Server returned field-level validation errors (422)
    if (e.fieldErrors && Object.keys(e.fieldErrors).length > 0) {
      errors.value = { ...errors.value, ...e.fieldErrors }
      notify('error', 'Please fix the errors below before saving.')
    } else {
      notify('error', store.error ?? e.message)
    }
  }
}

function handleClear() {
  form.value = emptyForm()
  errors.value = {}
  notification.value = null
  emailChecked.value = false
  store.clear()
}

function notify(type, message) {
  notification.value = { type, message }
  if (type === 'success') setTimeout(() => (notification.value = null), 5000)
}
</script>

<template>
  <div class="page">
    <div class="card">
      <h1 class="card-title">Project Assignment Form</h1>
      <p class="card-subtitle">Complete your profile to get assigned to internal projects.</p>

      <!-- Top-level notification banner -->
      <Transition name="fade">
        <div v-if="notification" :class="['notification', notification.type]" role="alert">
          {{ notification.message }}
          <button class="notif-close" @click="notification = null" aria-label="Dismiss">×</button>
        </div>
      </Transition>

      <form @submit.prevent="handleSubmit" novalidate>

        <!-- Full Name -->
        <div class="field">
          <label for="full_name">Full Name</label>
          <input
            id="full_name"
            v-model="form.full_name"
            type="text"
            placeholder="Jane Doe"
            :class="{ 'input-error': errors.full_name }"
            autocomplete="name"
          />
          <p v-if="errors.full_name" class="error-msg" role="alert">{{ errors.full_name }}</p>
        </div>

        <!-- Email -->
        <div class="field">
          <label for="email">
            Email Address
            <span v-if="store.loading" class="badge loading">Looking up…</span>
            <span v-else-if="emailLocked" class="badge locked">Profile loaded</span>
          </label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="jane@company.com"
            :readonly="emailLocked"
            :class="{ 'input-locked': emailLocked, 'input-error': errors.email }"
            autocomplete="email"
            @blur="handleEmailBlur"
          />
          <p v-if="errors.email" class="error-msg" role="alert">{{ errors.email }}</p>
        </div>

        <!-- Experience Level -->
        <div class="field">
          <label for="experience_level">Experience Level</label>
          <select
            id="experience_level"
            v-model="form.experience_level"
            :class="{ 'input-error': errors.experience_level }"
          >
            <option value="">Select your level</option>
            <option value="junior">Junior (0–2 years)</option>
            <option value="mid">Mid-level (2–5 years)</option>
            <option value="senior">Senior (5+ years)</option>
          </select>
          <p v-if="errors.experience_level" class="error-msg" role="alert">{{ errors.experience_level }}</p>
        </div>

        <!-- Tech Stack -->
        <div class="field">
          <label for="tech_stack">Primary Technology Stack</label>
          <select
            id="tech_stack"
            v-model="form.tech_stack"
            :class="{ 'input-error': errors.tech_stack }"
          >
            <option value="">Choose one</option>
            <option value="backend">Backend Development</option>
            <option value="frontend">Frontend Development</option>
            <option value="fullstack">Full-Stack Development</option>
            <option value="data">Data Engineering</option>
            <option value="devops">DevOps</option>
            <option value="mobile">Mobile Development</option>
          </select>
          <p v-if="errors.tech_stack" class="error-msg" role="alert">{{ errors.tech_stack }}</p>
        </div>

        <!-- Available Projects — populated dynamically from the API -->
        <div class="field">
          <label for="projects">
            Available Projects
            <span class="hint">Hold Ctrl / ⌘ to select multiple</span>
          </label>
          <select
            id="projects"
            v-model="form.project_ids"
            multiple
            :class="['multi-select', { 'input-error': errors.project_ids }]"
          >
            <option v-if="projects.length === 0" disabled value="">Loading projects…</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">
              {{ p.name }}
            </option>
          </select>
          <p v-if="errors.project_ids" class="error-msg" role="alert">{{ errors.project_ids }}</p>
        </div>

        <!-- Preferred Duration -->
        <div class="field">
          <span class="field-label">Preferred Project Duration</span>
          <div :class="['radio-group', { 'group-error': errors.preferred_duration }]">
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="short" />
              Short-term (1–3 months)
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="medium" />
              Medium-term (3–6 months)
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.preferred_duration" value="long" />
              Long-term (6+ months)
            </label>
          </div>
          <p v-if="errors.preferred_duration" class="error-msg" role="alert">{{ errors.preferred_duration }}</p>
        </div>

        <!-- Additional Skills -->
        <div class="field">
          <label for="additional_skills">
            Additional Skills
            <span class="optional">optional</span>
          </label>
          <input
            id="additional_skills"
            v-model="form.additional_skills"
            type="text"
            placeholder="e.g. Python, Docker, React"
          />
        </div>

        <!-- Availability Confirmation -->
        <div class="field">
          <label :class="['checkbox-label', { 'label-error': errors.availability_confirmed }]">
            <input type="checkbox" v-model="form.availability_confirmed" />
            I confirm my availability for the selected projects
          </label>
          <p v-if="errors.availability_confirmed" class="error-msg" role="alert">
            {{ errors.availability_confirmed }}
          </p>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button type="submit" class="btn-primary" :disabled="store.loading">
            {{ store.loading ? 'Saving…' : isUpdate ? 'Update Profile' : 'Save Profile' }}
          </button>
          <button type="button" class="btn-secondary" @click="handleClear">Clear Form</button>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 2.5rem 1rem;
}

.card {
  width: 100%;
  max-width: 580px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 2.5rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-heading);
  margin-bottom: 0.4rem;
}

.card-subtitle {
  color: var(--color-text);
  opacity: 0.7;
  margin-bottom: 1.8rem;
}

.notification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.notification.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #6ee7b7;
}

.notification.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

.notif-close {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0;
  color: inherit;
  opacity: 0.6;
  flex-shrink: 0;
}
.notif-close:hover { opacity: 1; }

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 1.15rem;
}

.field label,
.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-heading);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.field input[type='text'],
.field input[type='email'],
.field select {
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--color-border-hover);
  border-radius: 6px;
  background: var(--color-background);
  color: var(--color-text);
  font-size: 0.95rem;
  transition: border-color 0.2s;
  width: 100%;
}

.field input:focus,
.field select:focus {
  outline: none;
  border-color: hsla(160, 100%, 37%, 0.8);
}

.input-error {
  border-color: #dc2626 !important;
}

.input-error:focus {
  border-color: #dc2626 !important;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.15);
}

.group-error {
  padding: 0.5rem 0.6rem;
  border: 1px solid #dc2626;
  border-radius: 6px;
}

.label-error {
  color: #dc2626 !important;
}

/* Inline error message under a field */
.error-msg {
  font-size: 0.8rem;
  color: #dc2626;
  margin: 0;
}

.input-locked {
  opacity: 0.65;
  cursor: not-allowed;
  background: var(--color-background-mute) !important;
}

.multi-select {
  height: 220px;
  padding: 0.25rem;
}

.multi-select option {
  padding: 0.4rem 0.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.multi-select option:checked {
  background: hsla(160, 100%, 37%, 0.15);
  color: var(--color-heading);
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: normal !important;
  color: var(--color-text) !important;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: normal !important;
  color: var(--color-text) !important;
}

.badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.1rem 0.45rem;
  border-radius: 9999px;
}

.badge.loading { background: #fef3c7; color: #92400e; }
.badge.locked  { background: #d1fae5; color: #065f46; }

.hint {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.55;
  font-weight: normal;
}

.optional {
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.5;
  font-style: italic;
  font-weight: normal;
}

.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.8rem;
}

button {
  padding: 0.6rem 1.4rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.2s, opacity 0.2s;
}

.btn-primary { background: hsla(160, 100%, 37%, 1); color: #fff; }
.btn-primary:hover:not(:disabled) { background: hsla(160, 100%, 30%, 1); }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.btn-secondary { background: transparent; color: var(--color-text); border-color: var(--color-border-hover); }
.btn-secondary:hover { background: var(--color-background-mute); }

/* ── Fade transition for notification ────────────────────── */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from,
.fade-leave-to     { opacity: 0; }
</style>
