/**
 * Client-Side Router
 * Simple vanilla JS routing without dependencies
 */

import { isAuthenticated } from '../services/auth.js'

// Lazy import routes
let loginPage, dashboardPage, searchPage, emergencyAccessPage, auditPage, notFoundPage

const BASE_PATH = '/'

/**
 * Route definitions
 */
const ROUTES = {
  '/': {
    path: '/',
    title: 'Login - aQuickRescue',
    requireAuth: false,
    requiredRoles: [],
    load: async () => {
      if (!loginPage) {
        const { createLoginPage } = await import('../pages/LoginPage.js')
        loginPage = createLoginPage
      }
      return loginPage
    }
  },
  '/login': {
    path: '/login',
    title: 'Login - aQuickRescue',
    requireAuth: false,
    requiredRoles: [],
    load: async () => {
      if (!loginPage) {
        const { createLoginPage } = await import('../pages/LoginPage.js')
        loginPage = createLoginPage
      }
      return loginPage
    }
  },

  '/dashboard': {
    path: '/dashboard',
    title: 'Dashboard - aQuickRescue',
    requireAuth: true,
    requiredRoles: [],
    load: async () => {
      if (!dashboardPage) {
        const { createDashboardPage } = await import('../pages/DashboardPage.js')
        dashboardPage = createDashboardPage
      }
      return dashboardPage
    }
  },

  '/search': {
    path: '/search',
    title: 'Search Patient - aQuickRescue',
    requireAuth: true,
    requiredRoles: ['FIRST_RESPONDER', 'EMERGENCY_PHYSICIAN', 'ADMIN'],
    load: async () => {
      if (!searchPage) {
        const { createSearchPage } = await import('../pages/SearchPatientPage.js')
        searchPage = createSearchPage
      }
      return searchPage
    }
  },

  '/emergency-access': {
    path: '/emergency-access',
    title: 'Emergency Access - aQuickRescue',
    requireAuth: true,
    requiredRoles: ['FIRST_RESPONDER', 'EMERGENCY_PHYSICIAN', 'ADMIN'],
    load: async () => {
      if (!emergencyAccessPage) {
        const { createEmergencyAccessPage } = await import('../pages/EmergencyAccessPage.js')
        emergencyAccessPage = createEmergencyAccessPage
      }
      return emergencyAccessPage
    }
  },

  '/audit': {
    path: '/audit',
    title: 'Audit Trail - aQuickRescue',
    requireAuth: true,
    requiredRoles: ['PATIENT', 'ADMIN'],
    load: async () => {
      if (!auditPage) {
        const { createAuditPage } = await import('../pages/AuditTrailPage.js')
        auditPage = createAuditPage
      }
      return auditPage
    }
  }
}

/**
 * Router class
 */
class Router {
  constructor() {
    this.currentPath = window.location.pathname.replace(BASE_PATH, '/') || '/'
    this.listeners = []
    this.setupEventListeners()
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Handle browser back/forward
    window.addEventListener('popstate', () => {
      this.currentPath = window.location.pathname.replace(BASE_PATH, '/') || '/'
      this.notifyListeners()
    })

    // Handle link clicks
    document.addEventListener('click', (e) => {
      const link = e.target.closest('[data-link]')
      if (link) {
        e.preventDefault()
        this.navigate(link.getAttribute('href'))
      }
    })
  }

  /**
   * Navigate to path
   */
  navigate(path) {
    if (path === this.currentPath) return

    const route = ROUTES[path]
    if (!route) {
      console.warn(`[Router] Route not found: ${path}`)
      this.currentPath = '/404'
    } else {
      // Check authentication
      if (route.requireAuth && !isAuthenticated()) {
        this.currentPath = '/login'
        return
      }

      this.currentPath = path
    }

    // Update browser history
    window.history.pushState(null, '', BASE_PATH + this.currentPath.slice(1))
    this.notifyListeners()
  }

  /**
   * Get current route
   */
  async getCurrentRoute() {
    let route = ROUTES[this.currentPath]

    // 1. Handle 404 falling back gracefully
    if (!route) {
      if (!notFoundPage) {
        const module = await import('../pages/NotFoundPage.js')
        // Check if it's named 'createNotFoundPage' or a default export
        notFoundPage = module.createNotFoundPage || module.default
      }
      return {
        path: '/404',
        render: notFoundPage === 'function' ? notFoundPage : notFoundPage.render,
        attachListeners: notFoundPage.attachListeners || null
      }
    }

    // Check authentication
    if (route.requireAuth && !isAuthenticated()) {
      route = ROUTES['/login']
    }

    // 2. Load the component module safely
    const component = await route.load()

    // 3. Fallback extraction logic
    // If 'component' is a function, we execute it. If it's an object, we use its render method.
    let renderFn = null
    let attachListenersFn = null

    if (component && typeof component === 'object') {
      renderFn = component.render
      attachListenersFn = component.attachListeners
    } else if (typeof component === 'function') {
      // If the component itself is a factory function, execute it to see if it returns an object
      const initialized = component()
      renderFn = typeof initialized === 'function' ? initialized : initialized.render
      attachListenersFn = initialized.attachListeners
    }

    if (typeof renderFn !== 'function') {
      throw new Error(`[Router] Route "${route.path}" resolved to a component missing a valid render method.`)
    }

    return {
      path: route.path,
      render: renderFn,
      attachListeners: attachListenersFn || null,
      title: route.title
    }
  }

  /**
   * Subscribe to route changes
   */
  subscribe(listener) {
    this.listeners.push(listener)
    return () => {
      this.listeners = this.listeners.filter((l) => l !== listener)
    }
  }

  /**
   * Notify all listeners
   */
  notifyListeners() {
    this.listeners.forEach((listener) => listener())
  }

  /**
   * Get current path
   */
  getCurrentPath() {
    return this.currentPath
  }
}

/**
 * Export singleton router instance
 */
export const router = new Router()

/**
 * Setup router initialization
 */
export function setupRouter() {
  console.log('[Router] âœ“ Router initialized')
}

/**
 * Link helper for templates
 */
export function link(path, text, className = '') {
  return `<a href="${path}" data-link data-nav-link class="nav-link ${className}">${text}</a>`
}
