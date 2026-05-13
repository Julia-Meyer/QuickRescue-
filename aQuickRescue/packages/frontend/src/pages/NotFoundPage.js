/**
 * 404 Not Found Page
 */

export const createNotFoundPage = {
  render() {
    return `
      <div class="container not-found-container">
        <div class="not-found-card">
          <h1>404</h1>
          <h2>Seite nicht gefunden</h2>
          <p>Die gesuchte Seite existiert nicht oder wurde gelöscht.</p>

          <div class="not-found-actions">
            <a href="/dashboard" class="btn btn-primary">
              📊 Zum Dashboard
            </a>
            <a href="/search" class="btn btn-secondary">
              🔍 Patient suchen
            </a>
          </div>

          <div class="not-found-help">
            <h3>Verfügbare Seiten:</h3>
            <ul>
              <li><a href="/dashboard" class="nav-link">📊 Dashboard</a></li>
              <li><a href="/search" class="nav-link">🔍 Patient suchen</a></li>
              <li><a href="/emergency-access" class="nav-link">🚨 Notfallzugriff</a></li>
              <li><a href="/audit" class="nav-link">📋 Audit-Trail</a></li>
            </ul>
          </div>
        </div>
      </div>
    `
  }
}

