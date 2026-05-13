/**
 * aQuickRescue Frontend - Main Entry Point
 * Vite + Vanilla JS + SQLite
 * Speckit Compliance: Performance, Security, Audit Logging
 */

import { initializeApp } from './app.js'
import { setupRouter } from './router/index.js'
import { initializeDatabase } from './services/db.js'
import { initializeAuthService } from './services/auth.js'
import { setupLogging } from './utils/logging.js'

/**
 * Application bootstrap sequence
 */
async function bootstrap() {
  try {
    // 1. Setup logging (Speckit compliance)
    setupLogging()
    console.log('[App] Initializing aQuickRescue Frontend v0.1.0')

    // 2. Initialize local SQLite database
    console.log('[App] Initializing local database...')
    await initializeDatabase()

    // 3. Initialize authentication service
    console.log('[App] Setting up authentication...')
    await initializeAuthService()

    // 4. Setup client-side routing
    console.log('[App] Setting up router...')
    setupRouter()

    // 5. Initialize main application
    console.log('[App] Mounting application...')
    initializeApp()

    console.log('[App] ✓ aQuickRescue Frontend ready')
  } catch (error) {
    console.error('[App] Bootstrap failed:', error)
    document.getElementById('root').innerHTML = `
      <div style="padding: 2rem; text-align: center; color: #dc2626;">
        <h1>Application Error</h1>
        <p>${error.message}</p>
      </div>
    `
  }
}

// Start application
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootstrap)
} else {
  bootstrap()
}

// Hot Module Replacement (Vite)
if (import.meta.hot) {
  import.meta.hot.accept()
}

