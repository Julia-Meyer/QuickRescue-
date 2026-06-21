import { getCurrentUser, isFirstResponder, isPatient, isAdmin } from '../services/auth.js'
import { formatRole, formatRelativeTime } from '../utils/formatters.js'
import { link } from '../router/index.js'

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
              ${link('/search', 'Zur Suche', 'btn btn-primary')}
            </div>

            <div class="dashboard-card">
              <h2>🚨 Notfallzugriff</h2>
              <p>Auf Patientendaten im Notfall zugreifen</p>
              ${link('/emergency-access', 'Zugriff anfordern', 'btn btn-primary')}
            </div>
          ` : ''}

          ${isPatient() ? `
            <div class="dashboard-card">
              <h2>📋 Meine Daten</h2>
              <p>Persönliche Notfalldaten verwalten</p>
              ${link('/profile', 'Zu Profil', 'btn btn-primary')}
            </div>

            <div class="dashboard-card">
              <h2>👁️ Zugriff-Verlauf</h2>
              <p>Sehen Sie, wer auf Ihre Daten zugegriffen hat</p>
              ${link('/audit', 'Audit-Trail ansehen', 'btn btn-primary')}
            </div>
          ` : ''}

          ${isAdmin() ? `
            <div class="dashboard-card">
              <h2>⚙️ Verwaltung</h2>
              <p>Benutzer und Systemverwaltung</p>
              ${link('/admin', 'Admin-Panel', 'btn btn-primary')}
            </div>

            <div class="dashboard-card">
              <h2>📊 Statistiken</h2>
              <p>Systemstatistiken und Berichte</p>
              ${link('/stats', 'Statistiken', 'btn btn-primary')}
            </div>

            <div class="dashboard-card">
              <h2>📋 Audit-Trail</h2>
              <p>Alle Systemzugriffe und Ereignisse</p>
              ${link('/audit', 'Audit-Trail', 'btn btn-primary')}
            </div>
          ` : ''}
          <div class="dashboard-card">
  <h2>🔍 Patientensuche</h2>
  <input type="text" id="patient-search-id" placeholder="ID oder Name eingeben...">
  <button id="search-btn" class="btn btn-primary">Suchen</button>
  <div id="search-results"></div> </div>
  
<div class="dashboard-card">
  <h2>👥 Patientenstatistik</h2>
  <p>Registrierte Patienten: <span id="patient-count">0</span></p>
  
  <h3>🚨 Letzte 5 Zugriffe</h3>
  <ul id="access-list">
    <li>Lade Zugriffe...</li>
  </ul>
</div>

<div class="dashboard-card">
  <h2>🔍 Patientensuche</h2>
  <input type="text" id="patient-search-id" placeholder="Patienten-ID eingeben...">
  <button id="search-btn" class="btn btn-primary">Suchen</button>
</div>

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
     async function loadDashboardData(element) {
  try {
    const response = await fetch('/api/v1/dashboard/data', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await response.json();

    // Patienten-Zahl aktualisieren
    const patientCountEl = element.querySelector('#patient-count');
    if (patientCountEl) patientCountEl.innerText = data.total_patients;

    attachListeners(element)
      {
  checkSystemStatus(element);

  const btn = element.querySelector('#search-btn');
  btn.addEventListener('click', async () => {
    const query = element.querySelector('#patient-search-id').value;

    // Anfrage an dein Backend schicken
    const response = await fetch(`/api/v1/patients/search?query=${query}`);
    const results = await response.json();

    // Die Ergebnisse anzeigen
    displayResults(element, results);
  });
}
    // Zugriffs-Liste aktualisieren
    const listEl = element.querySelector('#access-list');
    if (listEl) {
      listEl.innerHTML = data.recent_access.map(acc => `
        <li>${acc.patient_name} - ${new Date(acc.time).toLocaleString()}</li>
      `).join('');
    }
  } catch (error) {
    console.error("Fehler beim Laden der Dashboard-Daten:", error);
  }
}
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
function displayResults(element, patients) {
  const container = element.querySelector('#search-results');

  if (patients.length === 0) {
    container.innerHTML = "<p>Kein Patient gefunden.</p>";
    return;
  }

  container.innerHTML = patients.map(p => `
    <div class="result-card">
      <h4>${p.first_name} ${p.last_name}</h4>
      <p><strong>Allergien:</strong> ${p.allergies}</p>
      <p><strong>Medikamente:</strong> ${p.medications}</p>
      <p><strong>Vorerkrankungen:</strong> ${p.conditions}</p>
      <a href="tel:${p.emergency_contact_phone}" class="btn btn-danger">Notfallkontakt anrufen</a>
    </div>
  `).join('');
}