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

    if (!route) {
      // 404 route
      if (!notFoundPage) {
        const { createNotFoundPage } = await import('../pages/NotFoundPage.js')
        notFoundPage = createNotFoundPage
      }
      return {
        path: '/404',
        render: notFoundPage,
        attachListeners: null
      }
    }

    // Check authentication
    if (route.requireAuth && !isAuthenticated()) {
      route = ROUTES['/login']
    }

    const pageComponent = await route.load()
    return {
      path: route.path,
      render: pageComponent.render,
      attachListeners: pageComponent.attachListeners || null,
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
  console.log('[Router] ✓ Router initialized')
}

/**
 * Link helper for templates
 */
export function link(path, text, className = '') {
  return `<a href="${path}" data-link data-nav-link class="nav-link ${className}">${text}</a>`
}

