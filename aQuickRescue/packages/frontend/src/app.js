/**
 * aQuickRescue App - Main Application Component
 * Renders routing and layout
 */

import { router } from './router/index.js'
import { createHeader } from './components/Header.js'
import { createFooter } from './components/Footer.js'
import { store } from './state/store.js'

/**
 * Initialize and mount the main application
 */
export function initializeApp() {
  const root = document.getElementById('root')

  // Subscribe to store updates for reactive rendering
  store.subscribe(() => {
    render()
  })

  // Initial render
  render()

  function render() {
    const currentRoute = router.getCurrentRoute()
    const isAuthenticated = store.getState().isAuthenticated

    root.innerHTML = `
      <div class="app-container">
        ${createHeader()}
        <main class="app-main">
          ${currentRoute.render()}
        </main>
        ${createFooter()}
      </div>
    `

    // Attach event listeners after rendering
    attachEventListeners(root, currentRoute)
  }

  function attachEventListeners(element, route) {
    // Header navigation
    const navLinks = element.querySelectorAll('[data-nav-link]')
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        e.preventDefault()
        const path = link.getAttribute('href')
        router.navigate(path)
        render()
      })
    })

    // Route-specific event handlers
    if (route.attachListeners) {
      route.attachListeners(element)
    }
  }
}

/**
 * Global error handler
 */
window.addEventListener('error', (event) => {
  console.error('[App Error]', event.error)
})

/**
 * Global unhandled promise rejection handler
 */
window.addEventListener('unhandledrejection', (event) => {
  console.error('[Unhandled Promise]', event.reason)
})

