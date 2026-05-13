/**
 * Validation Utilities
 */

/**
 * Validate email
 */
export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return re.test(email)
}

/**
 * Validate password
 */
export function validatePassword(password) {
  // Min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/
  return re.test(password)
}

/**
 * Validate phone
 */
export function validatePhone(phone) {
  const re = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/
  return re.test(phone.replace(/\s/g, ''))
}

/**
 * Validate date of birth
 */
export function validateDateOfBirth(dob) {
  const date = new Date(dob)
  if (isNaN(date.getTime())) return false

  const today = new Date()
  const age = today.getFullYear() - date.getFullYear()

  // Must be at least 0 years old and at most 150 years old
  return age >= 0 && age <= 150
}

/**
 * Validate reason (min 10 chars)
 */
export function validateReason(reason) {
  return reason && reason.trim().length >= 10
}

/**
 * Validate emergency access request
 */
export function validateEmergencyAccessRequest(data) {
  const errors = {}

  if (!data.patient_id) {
    errors.patient_id = 'Patienten-ID erforderlich'
  }

  if (!validateReason(data.reason)) {
    errors.reason = 'Grund erforderlich (mindestens 10 Zeichen)'
  }

  if (!Array.isArray(data.requested_data) || data.requested_data.length === 0) {
    errors.requested_data = 'Mindestens ein Datentyp erforderlich'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}

/**
 * Validate login form
 */
export function validateLoginForm(data) {
  const errors = {}

  if (!data.username) {
    errors.username = 'Benutzername erforderlich'
  }

  if (!data.password) {
    errors.password = 'Passwort erforderlich'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}

/**
 * Validate patient search
 */
export function validatePatientSearch(data) {
  const errors = {}

  if (!data.first_name || data.first_name.trim().length < 2) {
    errors.first_name = 'Vorname erforderlich (min. 2 Zeichen)'
  }

  if (!data.last_name || data.last_name.trim().length < 2) {
    errors.last_name = 'Nachname erforderlich (min. 2 Zeichen)'
  }

  if (!validateDateOfBirth(data.date_of_birth)) {
    errors.date_of_birth = 'Gültiges Geburtsdatum erforderlich'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}

