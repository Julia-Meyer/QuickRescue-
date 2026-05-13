/**
 * Dashboard Page
 */

import { getCurrentUser, isFirstResponder, isPatient, isAdmin } from '../services/auth.js'
import { formatRole, formatRelativeTime } from '../utils/formatters.js'

export const createDashboardPage = {
  render() {
    const user = getCurrentUser()

    return `
      <div class="container dashboard-container">
        <div class="dashboard-header">
          <h1>Willkommen, ${user?.username}!</h1>
          <p class="subtitle">Notfallmedizinische Datenverwaltung - ${formatRole(user?.role)}</p>
        </div>

        <div class="dashboard-grid">
          ${isFirstResponder() ? `
            <div class="dashboard-card">
              <h2>🔍 Patient suchen</h2>
              <p>Nach Patienten nach Namen und Geburtsdatum suchen</p>
              <a href="/search" class="btn btn-primary">Zur Suche</a>
            </div>

            <div class="dashboard-card">
              <h2>🚨 Notfallzugriff</h2>
              <p>Auf Patientendaten im Notfall zugreifen</p>
              <a href="/emergency-access" class="btn btn-primary">Zugriff anfordern</a>
            </div>
          ` : ''}

          ${isPatient() ? `
            <div class="dashboard-card">
              <h2>📋 Meine Daten</h2>
              <p>Persönliche Notfalldaten verwalten</p>
              <a href="/profile" class="btn btn-primary">Zu Profil</a>
            </div>

            <div class="dashboard-card">
              <h2>👁️ Zugriff-Verlauf</h2>
              <p>Sehen Sie, wer auf Ihre Daten zugegriffen hat</p>
              <a href="/audit" class="btn btn-primary">Audit-Trail ansehen</a>
            </div>
          ` : ''}

          ${isAdmin() ? `
            <div class="dashboard-card">
              <h2>⚙️ Verwaltung</h2>
              <p>Benutzer und Systemverwaltung</p>
              <a href="/admin" class="btn btn-primary">Admin-Panel</a>
            </div>

            <div class="dashboard-card">
              <h2>📊 Statistiken</h2>
              <p>Systemstatistiken und Berichte</p>
              <a href="/stats" class="btn btn-primary">Statistiken</a>
            </div>

            <div class="dashboard-card">
              <h2>📋 Audit-Trail</h2>
              <p>Alle Systemzugriffe und Ereignisse</p>
              <a href="/audit" class="btn btn-primary">Audit-Trail</a>
            </div>
          ` : ''}

          <div class="dashboard-card info-card">
            <h3>ℹ️ Informationen</h3>
            <ul>
              <li><strong>Rolle:</strong> ${formatRole(user?.role)}</li>
              <li><strong>Benutzer-ID:</strong> <code>${user?.id}</code></li>
              <li><strong>Status:</strong> <span class="badge badge-success">🟢 Aktiv</span></li>
            </ul>
          </div>

          <div class="dashboard-card status-card">
            <h3>🏥 System-Status</h3>
            <div id="system-status">
              <p>Status wird geladen...</p>
            </div>
          </div>
        </div>
      </div>
    `
  },

  attachListeners(element) {
    // Check system status
    checkSystemStatus(element)
  }
}

/**
 * Check system status
 */
async function checkSystemStatus(element) {
  try {
    const response = await fetch('/api/v1/health')
    const data = await response.json()

    const statusDiv = element.querySelector('#system-status')
    if (statusDiv) {
      statusDiv.innerHTML = `
        <div class="status-item">
          <span>API Status:</span>
          <span class="badge badge-success">🟢 ${data.status}</span>
        </div>
        <div class="status-item">
          <span>Database:</span>
          <span class="badge badge-success">🟢 Verbunden</span>
        </div>
        <div class="status-item small">
          <span>Zuletzt aktualisiert:</span>
          <span>${new Date(data.timestamp).toLocaleTimeString('de-DE')}</span>
        </div>
      `
    }
  } catch (error) {
    const statusDiv = element.querySelector('#system-status')
    if (statusDiv) {
      statusDiv.innerHTML = `
        <div class="status-item">
          <span class="badge badge-danger">🔴 Fehler</span>
        </div>
      `
    }
  }
}

