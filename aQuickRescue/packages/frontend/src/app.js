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

  // 1. Turned this into an ASYNC function so we can await the router resolution
  async function render() {
    try {
      // 2. Await the lazy-loaded route object cleanly
      const currentRoute = await router.getCurrentRoute()
      const isAuthenticated = store.getState().isAuthenticated

      // Safety check: ensure render exists before execution
      if (!currentRoute || typeof currentRoute.render !== 'function') {
        throw new Error(`The matched route does not have a valid render function.`);
      }

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

    } catch (error) {
      console.error('[App Bootstrap Render Error]', error)
      root.innerHTML = `
        <div style="padding: 2rem; text-align: center; color: #dc2626;">
          <h1>Application Render Error</h1>
          <p>${error.message}</p>
        </div>
      `
    }
  }

  function attachEventListeners(element, route) {
    // Header navigation
    const navLinks = element.querySelectorAll('[data-nav-link]')
    navLinks.forEach(link => {
      link.addEventListener('click', async (e) => { // Made async to support render loop smoothly
        e.preventDefault()
        const path = link.getAttribute('href')
        router.navigate(path)
        await render()
      })
    })

    // Route-specific event handlers
    if (route && route.attachListeners) {
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