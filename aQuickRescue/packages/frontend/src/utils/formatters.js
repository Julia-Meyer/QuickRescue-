/**
 * Formatting Utilities
 */

/**
 * Format date
 */
export function formatDate(date, format = 'DD.MM.YYYY HH:MM') {
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('MM', minutes)
}

/**
 * Format relative time
 */
export function formatRelativeTime(date) {
  const seconds = Math.floor((new Date() - new Date(date)) / 1000)

  if (seconds < 60) return 'vor wenigen Sekunden'
  if (seconds < 3600) return `vor ${Math.floor(seconds / 60)} Minuten`
  if (seconds < 86400) return `vor ${Math.floor(seconds / 3600)} Stunden`
  if (seconds < 2592000) return `vor ${Math.floor(seconds / 86400)} Tagen`

  return formatDate(date)
}

/**
 * Format phone number
 */
export function formatPhone(phone) {
  if (!phone) return ''
  const cleaned = phone.replace(/\D/g, '')
  if (cleaned.length === 10) return cleaned.replace(/(\d{2})(\d{3})(\d{5})/, '+$1 $2 $3')
  if (cleaned.length === 11) return cleaned.replace(/(\d{2})(\d{4})(\d{5})/, '+$1 $2 $3')
  return phone
}

/**
 * Format criticality level
 */
export function formatCriticality(level) {
  const map = {
    'low': '🟢 Niedrig',
    'medium': '🟡 Mittel',
    'high': '🔴 Hoch',
    'unknown': '⚪ Unbekannt'
  }
  return map[level?.toLowerCase()] || level
}

/**
 * Truncate text
 */
export function truncate(text, length = 50) {
  if (!text) return ''
  return text.length > length ? text.slice(0, length) + '...' : text
}

/**
 * Format role
 */
export function formatRole(role) {
  const map = {
    'PATIENT': 'Patient',
    'FIRST_RESPONDER': 'Ersthelfer',
    'EMERGENCY_PHYSICIAN': 'Notfallarzt',
    'ADMIN': 'Administrator'
  }
  return map[role] || role
}

/**
 * Format status badge
 */
export function formatStatus(status) {
  const map = {
    'SUCCESS': '<span class="badge badge-success">✓ Erfolgreich</span>',
    'DENIED': '<span class="badge badge-danger">✗ Abgelehnt</span>',
    'FAILED': '<span class="badge badge-danger">✗ Fehler</span>',
    'PENDING': '<span class="badge badge-warning">⏳ Ausstehend</span>',
    'GRANTED': '<span class="badge badge-success">✓ Gewährt</span>',
    'EXPIRED': '<span class="badge badge-secondary">⏱ Abgelaufen</span>'
  }
  return map[status] || status
}

