/**
 * Authentication Service
 * Manages authentication state and tokens
 */

import { store } from '../state/store.js'
import { saveMetadata, getMetadata } from '../services/db.js'

const TOKEN_KEY = 'aQuickRescue_token'
const USER_KEY = 'aQuickRescue_user'

/**
 * Initialize authentication service
 */
export async function initializeAuthService() {
  try {
    // Check for existing token in localStorage
    const token = localStorage.getItem(TOKEN_KEY)
    const userJson = localStorage.getItem(USER_KEY)

    if (token && userJson) {
      const user = JSON.parse(userJson)
      store.getState().setAuth(token, user)
      console.log('[Auth] ✓ User restored from localStorage')
      return true
    }

    console.log('[Auth] No existing auth session')
    return false
  } catch (error) {
    console.error('[Auth] Initialization failed:', error)
    clearAuth()
    return false
  }
}

/**
 * Save authentication tokens
 */
export function saveAuth(token, user) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    store.getState().setAuth(token, user)
  } catch (error) {
    console.error('[Auth] Failed to save auth:', error)
    throw error
  }
}

/**
 * Clear authentication (logout)
 */
export function clearAuth() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    store.getState().logout()
  } catch (error) {
    console.error('[Auth] Failed to clear auth:', error)
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated() {
  return store.getState().isAuthenticated
}

/**
 * Get current user
 */
export function getCurrentUser() {
  return store.getState().user
}

/**
 * Get current token
 */
export function getToken() {
  return store.getState().token
}

/**
 * Check if user has specific role
 */
export function hasRole(role) {
  const currentRole = store.getState().role
  if (!currentRole) return false

  if (typeof role === 'string') {
    return currentRole === role
  }

  if (Array.isArray(role)) {
    return role.includes(currentRole)
  }

  return false
}

/**
 * Check if user is first responder
 */
export function isFirstResponder() {
  return hasRole(['FIRST_RESPONDER', 'EMERGENCY_PHYSICIAN', 'ADMIN'])
}

/**
 * Check if user is patient
 */
export function isPatient() {
  return hasRole('PATIENT')
}

/**
 * Check if user is admin
 */
export function isAdmin() {
  return hasRole('ADMIN')
}

/**
 * Decode JWT token (without verification - frontend only)
 */
export function decodeToken(token) {
  try {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  } catch (error) {
    console.error('[Auth] Failed to decode token:', error)
    return null
  }
}

/**
 * Check if token is expired
 */
export function isTokenExpired(token) {
  try {
    const decoded = decodeToken(token)
    if (!decoded || !decoded.exp) return true

    const expirationTime = decoded.exp * 1000
    return Date.now() >= expirationTime
  } catch (error) {
    return true
  }
}

/**
 * Get time until token expires
 */
export function getTokenExpiresIn() {
  try {
    const token = store.getState().token
    if (!token) return 0

    const decoded = decodeToken(token)
    if (!decoded || !decoded.exp) return 0

    const expirationTime = decoded.exp * 1000
    const timeLeft = expirationTime - Date.now()

    return Math.max(0, timeLeft)
  } catch (error) {
    return 0
  }
}

/**
 * Format permissions display
 */
export function formatUserRole(role) {
  const roleMap = {
    PATIENT: 'Patient',
    FIRST_RESPONDER: 'First Responder',
    EMERGENCY_PHYSICIAN: 'Emergency Physician',
    ADMIN: 'Administrator'
  }
  return roleMap[role] || role
}

