/**
 * Footer Component
 */

export function createFooter() {
  return `
    <footer class="footer">
      <div class="footer-container">
        <div class="footer-content">
          <p>&copy; 2026 aQuickRescue - Notfalldatenverwaltung</p>
          <div class="footer-links">
            <a href="#" class="footer-link">Datenschutz</a>
            <span class="separator">•</span>
            <a href="#" class="footer-link">Nutzungsbedingungen</a>
            <span class="separator">•</span>
            <span class="version">v0.1.0</span>
          </div>
        </div>
        <div class="footer-status">
          <span id="api-status" class="status-indicator" title="API Status">
            🟢 Online
          </span>
        </div>
      </div>
    </footer>
  `
}

