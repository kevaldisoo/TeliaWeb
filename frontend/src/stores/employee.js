import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api/index.js'

const STORAGE_KEY = 'pa_employee_id'

export const useEmployeeStore = defineStore('employee', () => {
  const employee = ref(null)
  const loading = ref(false)
  const error = ref(null)

  /** On app mount, check if there is a stored employee ID and load that profile. */
  async function loadStoredEmployee() {
    const id = localStorage.getItem(STORAGE_KEY)
    if (!id) return

    loading.value = true
    try {
      employee.value = await api.getEmployee(id)
    } catch {
      // Stored ID no longer valid (e.g. row deleted) — clean up silently.
      localStorage.removeItem(STORAGE_KEY)
    } finally {
      loading.value = false
    }
  }

  /** Look up a profile by email. Returns the employee or null if not found. */
  async function lookupByEmail(email) {
    loading.value = true
    error.value = null
    try {
      const found = await api.getEmployeeByEmail(email)
      employee.value = found
      localStorage.setItem(STORAGE_KEY, found.id)
      return found
    } catch (e) {
      if (!e.message.toLowerCase().includes('not found')) {
        error.value = e.message
      }
      return null
    } finally {
      loading.value = false
    }
  }

  /** Create or update the employee profile depending on whether one is loaded. */
  async function saveEmployee(data) {
    loading.value = true
    error.value = null
    try {
      if (employee.value?.id) {
        employee.value = await api.updateEmployee(employee.value.id, data)
      } else {
        employee.value = await api.createEmployee(data)
        localStorage.setItem(STORAGE_KEY, employee.value.id)
      }
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      loading.value = false
    }
  }

  /** Clear the local state and remove the stored ID (used by Clear Form). */
  function clear() {
    employee.value = null
    error.value = null
    localStorage.removeItem(STORAGE_KEY)
  }

  return { employee, loading, error, loadStoredEmployee, lookupByEmail, saveEmployee, clear }
})
