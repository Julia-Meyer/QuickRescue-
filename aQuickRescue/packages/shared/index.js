/**
 * Shared Package - Types and Utilities
 * Shared between Frontend and Backend
 */

// User Types
export const UserRole = {
  PATIENT: 'PATIENT',
  FIRST_RESPONDER: 'FIRST_RESPONDER',
  EMERGENCY_PHYSICIAN: 'EMERGENCY_PHYSICIAN',
  ADMIN: 'ADMIN'
}

// Emergency Access Status
export const EmergencyAccessStatus = {
  GRANTED: 'GRANTED',
  DENIED: 'DENIED',
  EXPIRED: 'EXPIRED'
}

// Audit Action Types
export const AuditAction = {
  CREATE: 'CREATE',
  READ: 'READ',
  UPDATE: 'UPDATE',
  DELETE: 'DELETE',
  EMERGENCY_ACCESS: 'EMERGENCY_ACCESS',
  PATIENT_SEARCH: 'PATIENT_SEARCH'
}

// Resource Types
export const ResourceType = {
  PATIENT: 'Patient',
  ALLERGY: 'AllergyIntolerance',
  MEDICATION: 'Medication',
  CONTACT: 'Contact',
  AUDIT_EVENT: 'AuditEvent'
}

// API Response Status
export const ApiStatus = {
  SUCCESS: 'SUCCESS',
  ERROR: 'ERROR',
  PENDING: 'PENDING'
}

// Constants
export const Constants = {
  ACCESS_TOKEN_EXPIRE_MINUTES: 15,
  REFRESH_TOKEN_EXPIRE_DAYS: 30,
  SEARCH_TIMEOUT_MS: 5000,
  EMERGENCY_ACCESS_TIMEOUT_MS: 5000,
  API_VERSION: 'v1'
}

/**
 * Validates if user has required role
 */
export function hasRole(userRole, requiredRoles) {
  if (typeof requiredRoles === 'string') {
    return userRole === requiredRoles
  }
  if (Array.isArray(requiredRoles)) {
    return requiredRoles.includes(userRole)
  }
  return false
}

/**
 * Checks if user is first responder or higher
 */
export function isFirstResponder(userRole) {
  return hasRole(userRole, [
    UserRole.FIRST_RESPONDER,
    UserRole.EMERGENCY_PHYSICIAN,
    UserRole.ADMIN
  ])
}

/**
 * Checks if user is patient
 */
export function isPatient(userRole) {
  return userRole === UserRole.PATIENT
}

/**
 * Checks if user is admin
 */
export function isAdmin(userRole) {
  return userRole === UserRole.ADMIN
}

export default {
  UserRole,
  EmergencyAccessStatus,
  AuditAction,
  ResourceType,
  ApiStatus,
  Constants,
  hasRole,
  isFirstResponder,
  isPatient,
  isAdmin
}

