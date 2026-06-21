/**
 * API Client Service
 * Handles all backend communication with FastAPI
 */

import axios from 'axios'
import { store } from '../state/store.js'
import { logAction } from '../utils/logging.js'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
const API_VERSION = 'v1'


/**
 * Axios instance with interceptors
 */
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/${API_VERSION}`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Request interceptor - Add auth token
 */
apiClient.interceptors.request.use(
  (config) => {
    const token = store.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/**
 * Response interceptor - Handle errors & refresh tokens
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      store.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

/**
 * Authentication API
 */
export const authAPI = {
  async login(username, password) {
    try {
      const response = await apiClient.post('/auth/login', { username, password })
      store.getState().setAuth(response.data.access_token, response.data.user)
      logAction('LOGIN', 'SUCCESS')
      return response.data
    } catch (error) {
      logAction('LOGIN', 'FAILED', error.message)
      throw error
    }
  },

  async logout() {
    store.getState().logout()
    logAction('LOGOUT', 'SUCCESS')
  },

  async register(userData) {
    try {
      const response = await apiClient.post('/auth/register', userData)
      logAction('REGISTER', 'SUCCESS')
      return response.data
    } catch (error) {
      logAction('REGISTER', 'FAILED', error.message)
      throw error
    }
  },

  async refreshToken() {
    try {
      const response = await apiClient.post('/auth/refresh')
      store.getState().setAuth(response.data.access_token, store.getState().user)
      return response.data
    } catch (error) {
      throw error
    }
  }
}

/**
 * Patient Search API
 */
export const patientAPI = {
  async search(firstName, lastName, dateOfBirth) {
    try {
      store.getState().setLoading(true)
      const response = await apiClient.get('/patients/search', {
        params: {
          first_name: firstName,
          last_name: lastName,
          date_of_birth: dateOfBirth
        }
      })

      store.getState().setSearchResults(response.data.patients || [])
      logAction('PATIENT_SEARCH', 'SUCCESS', `Found ${response.data.patients?.length || 0} patients`)

      return response.data
    } catch (error) {
      logAction('PATIENT_SEARCH', 'FAILED', error.message)
      throw error
    } finally {
      store.getState().setLoading(false)
    }
  },

  async getPatientProfile(patientId) {
    try {
      const response = await apiClient.get(`/patients/${patientId}`)
      logAction('GET_PATIENT_PROFILE', 'SUCCESS')
      return response.data
    } catch (error) {
      logAction('GET_PATIENT_PROFILE', 'FAILED', error.message)
      throw error
    }
  }
}

/**
 * Emergency Access API
 */
export const emergencyAPI = {
  async requestAccess(patientId, reason, requestedData, gpsLocation = null) {
    try {
      store.getState().setLoading(true)

      const response = await apiClient.post('/emergency-access', {
        patient_id: patientId,
        reason,
        requested_data: requestedData,
        gps_location: gpsLocation
      })

      store.getState().addEmergencyAccess(response.data)
      logAction('EMERGENCY_ACCESS_REQUEST', 'SUCCESS', reason)

      return response.data
    } catch (error) {
      logAction('EMERGENCY_ACCESS_REQUEST', 'FAILED', error.message)
      throw error
    } finally {
      store.getState().setLoading(false)
    }
  },

  async getAccessHistory(limit = 50) {
    try {
      const response = await apiClient.get('/emergency-access/history', {
        params: { limit }
      })

      store.getState().setEmergencyAccessHistory(response.data)
      return response.data
    } catch (error) {
      console.error('[API] Failed to get emergency access history:', error)
      throw error
    }
  }
}

/**
 * Audit Trail API
 */
export const auditAPI = {
  async getAuditTrail(limit = 50, filter = {}) {
    try {
      store.getState().setLoading(true)

      const response = await apiClient.get('/audit-trail', {
        params: {
          limit,
          ...filter
        }
      })

      store.getState().setAuditTrail(response.data)
      return response.data
    } catch (error) {
      console.error('[API] Failed to get audit trail:', error)
      throw error
    } finally {
      store.getState().setLoading(false)
    }
  },

  async getAuditEvent(eventId) {
    try {
      const response = await apiClient.get(`/audit-trail/${eventId}`)
      return response.data
    } catch (error) {
      console.error('[API] Failed to get audit event:', error)
      throw error
    }
  }
}

/**
 * Health Check API
 */
export const healthAPI = {
  async check() {
    try {
      const response = await apiClient.get('/health')
      return response.data
    } catch (error) {
      console.error('[API] Health check failed:', error)
      return { status: 'unhealthy', error: error.message }
    }
  }
}

/**
 * Export API client instance for custom requests
 */
export default apiClient

