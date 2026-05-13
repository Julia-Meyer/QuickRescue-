/**
 * Audit Trail Page
 */

import { auditAPI } from '../services/api.js'
import { store } from '../state/store.js'
import { formatDate, formatStatus } from '../utils/formatters.js'

export const createAuditPage = {
  render() {
    const auditTrail = store.getState().auditTrail
    const loading = store.getState().loading

    return `
      <div class="container audit-container">
        <div class="audit-header">
          <h1>📋 Audit-Trail</h1>
          <p>Alle Zugriffe und Änderungen an Patientendaten</p>
        </div>

        <div class="audit-filters">
          <div class="filter-group">
            <label for="action-filter">Aktion:</label>
            <select id="action-filter" class="filter-select">
              <option value="">Alle Aktionen</option>
              <option value="PATIENT_SEARCH">Patient-Suche</option>
              <option value="EMERGENCY_ACCESS_GRANTED">Notfallzugriff gewährt</option>
              <option value="EMERGENCY_ACCESS_DENIED">Notfallzugriff abgelehnt</option>
              <option value="READ">Daten gelesen</option>
              <option value="UPDATE">Daten geändert</option>
            </select>
          </div>

          <div class="filter-group">
            <label for="status-filter">Status:</label>
            <select id="status-filter" class="filter-select">
              <option value="">Alle Status</option>
              <option value="SUCCESS">✓ Erfolgreich</option>
              <option value="DENIED">✗ Abgelehnt</option>
              <option value="FAILED">✗ Fehler</option>
            </select>
          </div>

          <button id="refresh-btn" class="btn btn-sm btn-primary">
            🔄 Aktualisieren
          </button>
        </div>

        <div class="audit-list">
          ${auditTrail.length > 0 ? `
            <div class="table-responsive">
              <table class="audit-table">
                <thead>
                  <tr>
                    <th>Zeitstempel</th>
                    <th>Benutzer</th>
                    <th>Aktion</th>
                    <th>Status</th>
                    <th>Grund</th>
                  </tr>
                </thead>
                <tbody>
                  ${auditTrail.map((entry) => `
                    <tr class="audit-entry" data-entry-id="${entry.id}">
                      <td class="timestamp">
                        ${formatDate(entry.timestamp, 'DD.MM.YYYY HH:MM')}
                      </td>
                      <td class="user">
                        ${entry.user || 'System'}
                      </td>
                      <td class="action">
                        ${entry.action}
                      </td>
                      <td class="status">
                        ${formatStatus(entry.status)}
                      </td>
                      <td class="reason">
                        ${entry.reason || '-'}
                      </td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : `
            <div class="empty-state">
              <p>${loading ? 'Daten werden geladen...' : 'Keine Audit-Einträge gefunden'}</p>
            </div>
          `}
        </div>

        <div class="audit-export">
          <button id="export-btn" class="btn btn-sm btn-secondary">
            📥 Exportieren (CSV)
          </button>
        </div>
      </div>
    `
  },

  attachListeners(element) {
    const refreshBtn = element.querySelector('#refresh-btn')
    const exportBtn = element.querySelector('#export-btn')
    const actionFilter = element.querySelector('#action-filter')
    const statusFilter = element.querySelector('#status-filter')

    if (refreshBtn) {
      refreshBtn.addEventListener('click', async () => {
        try {
          const filter = {
            action: actionFilter?.value || undefined,
            status: statusFilter?.value || undefined
          }
          await auditAPI.getAuditTrail(50, filter)
        } catch (error) {
          console.error('Failed to refresh audit trail:', error)
        }
      })
    }

    if (exportBtn) {
      exportBtn.addEventListener('click', () => {
        const auditTrail = store.getState().auditTrail
        const csv = auditTrailToCSV(auditTrail)
        downloadCSV(csv, 'audit-trail.csv')
      })
    }
  }
}

/**
 * Convert audit trail to CSV
 */
function auditTrailToCSV(auditTrail) {
  const headers = ['Zeitstempel', 'Benutzer', 'Aktion', 'Status', 'Grund']
  const rows = auditTrail.map((entry) => [
    new Date(entry.timestamp).toLocaleString('de-DE'),
    entry.user || 'System',
    entry.action,
    entry.status,
    entry.reason || ''
  ])

  const csv = [
    headers.join(','),
    ...rows.map((row) => row.map((cell) => `"${cell}"`).join(','))
  ].join('\n')

  return csv
}

/**
 * Download CSV file
 */
function downloadCSV(csv, filename) {
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)

  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

