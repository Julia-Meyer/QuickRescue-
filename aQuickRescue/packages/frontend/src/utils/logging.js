/**
 * Logging Utilities
 * Speckit compliance - structured logging
 */

import { saveAuditEvent } from '../services/db.js'

/**
 * Set up logging infrastructure
 */
export function setupLogging() {
  // Override console methods for structured logging
  const originalLog = console.log
  const originalError = console.error
  const originalWarn = console.warn

  console.log = function (...args) {
    logStructured('INFO', args)
    originalLog.apply(console, args)
  }

  console.error = function (...args) {
    logStructured('ERROR', args)
    originalError.apply(console, args)
  }

  console.warn = function (...args) {
    logStructured('WARN', args)
    originalWarn.apply(console, args)
  }

  console.log('[Logging] ✓ Logging initialized')
}

/**
 * Structured logging function
 */
function logStructured(level, args) {
  const timestamp = new Date().toISOString()
  const message = args.map((arg) => {
    if (typeof arg === 'object') {
      return JSON.stringify(arg)
    }
    return String(arg)
  }).join(' ')

  const logEntry = {
    timestamp,
    level,
    message,
    userAgent: navigator.userAgent,
    url: window.location.href
  }

  // Send to backend asynchronously (don't block)
  sendLogToBackend(logEntry).catch(() => {
    // Silently fail - don't interfere with app
  })
}

/**
 * Log user actions locally
 */
export async function logAction(action, status = 'SUCCESS', details = '') {
  try {
    const event = {
      action,
      status,
      details,
      timestamp: new Date().toISOString(),
      url: window.location.href
    }

    // Save to local database
    await saveAuditEvent({
      user_id: null, // Will be set during sync
      patient_id: null,
      action,
      resource_type: 'FrontendAction',
      resource_id: action,
      reason: details
    })

    console.log(`[Action] ${action} - ${status}`)
  } catch (error) {
    console.error('[Logging] Failed to log action:', error)
  }
}

/**
 * Send log to backend
 */
async function sendLogToBackend(logEntry) {
  try {
    const token = localStorage.getItem('aQuickRescue_token')
    if (!token) return // Not authenticated yet

    await fetch('/api/v1/logs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(logEntry)
    })
  } catch (error) {
    // Silently fail
  }
}

/**
 * Performance tracking
 */
export class PerformanceTracker {
  constructor(label) {
    this.label = label
    this.startTime = performance.now()
    this.marks = []
  }

  mark(name) {
    const elapsed = performance.now() - this.startTime
    this.marks.push({ name, elapsed })
  }

  end() {
    const total = performance.now() - this.startTime
    const summary = {
      label: this.label,
      total: `${total.toFixed(2)}ms`,
      marks: this.marks.map((m) => `${m.name}: ${m.elapsed.toFixed(2)}ms`)
    }
    console.log('[Perf]', summary)
    return total
  }
}

/**
 * Error handler for promises
 */
export function handleError(error, context = '') {
  console.error(`[Error][${context}] ${error.message}`, error)
  logAction('ERROR', 'FAILED', `${context}: ${error.message}`)
}

