/**
 * Header Component
 */

import { store } from '../state/store.js'
import { isAuthenticated, getCurrentUser, formatUserRole } from '../services/auth.js'
import { link } from '../router/index.js'

export function createHeader() {
  const isAuth = isAuthenticated()
  const user = getCurrentUser()

  return `
    <header class="header">
      <div class="header-container">
        <div class="header-brand">
          <h1>
            <a href="/dashboard" data-link class="brand-link">
              🚨 aQuickRescue
            </a>
          </h1>
        </div>

        <nav class="header-nav">
          ${isAuth ? `
            <div class="nav-authenticated">
              ${user?.role?.includes('RESPONDER') || user?.role?.includes('PHYSICIAN') ? `
                <a href="/search" data-link class="nav-link">🔍 Patient suchen</a>
                <a href="/emergency-access" data-link class="nav-link">🚨 Notfallzugriff</a>
              ` : ''}

              ${user?.role === 'PATIENT' ? `
                <a href="/audit" data-link class="nav-link">📋 Audit-Trail</a>
              ` : ''}

              ${user?.role === 'ADMIN' ? `
                <a href="/audit" data-link class="nav-link">📋 Audit-Trail</a>
                <a href="/admin" data-link class="nav-link">⚙️ Verwaltung</a>
              ` : ''}

              <div class="nav-user">
                <span class="user-badge">${user?.username}</span>
                <span class="user-role">${formatUserRole(user?.role)}</span>
                <button id="logout-btn" class="btn btn-sm btn-secondary">Abmelden</button>
              </div>
            </div>
          ` : `
            <div class="nav-anonymous">
              <a href="/login" data-link class="nav-link">Anmelden</a>
            </div>
          `}
        </nav>
      </div>
    </header>
  `
}

/**
 * Attach header event listeners
 */
export function attachHeaderListeners() {
  const logoutBtn = document.getElementById('logout-btn')
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      store.getState().logout()
      window.location.href = '/login'
    })
  }
}

