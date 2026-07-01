import { getCurrentUser, isFirstResponder, isPatient, isAdmin } from '../services/auth.js'
import { formatRole } from '../utils/formatters.js'
import { link } from '../router/index.js'

export const createDashboardPage = {
  render() {
    const user = getCurrentUser()

    // Selbst-Initialisierung nach dem Rendern im DOM-Baum
    setTimeout(() => {
      const element = document.querySelector('.dashboard-container');
      if (element) this.attachListeners(element);
    }, 100);

    return `
      <style>
        .search-hero-card {
          grid-column: 1 / -1;
          background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
          border-left: 6px solid #0284c7;
          padding: 30px !important;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05) !important;
        }
        .search-container-wrapper {
          display: flex;
          gap: 15px;
          margin-top: 15px;
          max-width: 800px;
        }
        .large-search-input {
          flex: 1;
          padding: 14px 20px !important;
          font-size: 16px !important;
          border: 2px solid #cbd5e1 !important;
          border-radius: 10px !important;
          outline: none;
          color: #1e293b !important;
          transition: all 0.2s ease;
        }
        .large-search-input:focus {
          border-color: #0284c7 !important;
          box-shadow: 0 0 0 4px rgba(2, 132, 199, 0.15);
        }
        .large-search-btn {
          padding: 0 30px !important;
          font-size: 16px !important;
          font-weight: 600 !important;
          border-radius: 10px !important;
          background-color: #0284c7 !important;
          color: white !important;
          transition: all 0.2s ease !important;
          cursor: pointer;
          border: none;
        }
        .large-search-btn:hover {
          background-color: #0369a1 !important;
          transform: translateY(-1px);
        }
        .progress-bar-container {
          width: 100%;
          background-color: #e2e8f0;
          height: 8px;
          border-radius: 4px;
          overflow: hidden;
          margin-top: 4px;
          margin-bottom: 12px;
        }
        .progress-bar-fill {
          height: 100%;
          border-radius: 4px;
          transition: width 0.6s ease-in-out;
        }
        .stats-flex-row {
          display: flex;
          justify-content: space-between;
          font-size: 14px;
          color: #334155;
        }
        .call-btn {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          text-decoration: none;
          padding: 6px 14px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 600;
          margin-top: 6px;
          transition: background-color 0.2s;
        }
        .call-btn-blue { background-color: #0284c7; color: white; }
        .call-btn-blue:hover { background-color: #0369a1; }
        .call-btn-red { background-color: #dc2626; color: white; }
        .call-btn-red:hover { background-color: #b91c1c; }
        .patient-row-item {
          border: 1px solid #cbd5e1;
          padding: 15px;
          margin-bottom: 10px;
          border-radius: 8px;
          background: #f8fafc;
          display: flex;
          justify-content: space-between;
          align-items: center;
          cursor: pointer;
          color: #1e293b !important;
        }
      </style>

      <div class="container dashboard-container">
        <div class="dashboard-header">
          <h1>Willkommen, ${user?.username}!</h1>
          <p class="subtitle">Notfallmedizinische Datenverwaltung - ${formatRole(user?.role)}</p>
        </div>

        <div class="dashboard-grid">
          
          <div class="dashboard-card search-hero-card">
            <h2 style="font-size: 24px; margin-bottom: 5px; color: #1e293b;">🔍 Zentrale Patientenschnellsuche</h2>
            <p style="color: #64748b;">Geben Sie die Patienten-ID, den Vor- oder Nachnamen ein, um die digitale Notfallakte sofort zu laden.</p>
            
            <div class="search-container-wrapper">
              <input type="text" id="patient-search-id" class="large-search-input" placeholder="Z. B. 'Max', 'Müller' oder die ID '1'...">
              <button id="search-btn" class="large-search-btn">Patient Akte laden</button>
            </div>
            
            <div id="search-results" style="margin-top: 15px;"></div> 
          </div>

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
          ` : ''}
  
          <div class="dashboard-card">
            <h2>👥 Patientenstatistik</h2>
            <p>Registrierte Patienten: <span id="patient-count">0</span></p>
            <h3>🚨 Letzte 5 Zugriffe</h3>
            <ul id="access-list">
              <li>Lade Zugriffe...</li>
            </ul>
          </div>

          <div class="dashboard-card">
            <h2>📊 Häufigste Allergierisiken</h2>
            <div id="analytics-allergies-list">
              <p style="color: #64748b;">Lade Allergiedaten...</p>
            </div>
          </div>

          <div class="dashboard-card">
            <h2>📋 Meiste Vorerkrankungen</h2>
            <div id="analytics-conditions-list">
              <p style="color: #64748b;">Lade Diagnosen...</p>
            </div>
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
    loadDashboardData(element);
    loadVisualAnalytics(element);
    checkSystemStatus(element);

    const btn = element.querySelector('#search-btn');
    const input = element.querySelector('#patient-search-id');

    const performSearchAction = async () => {
      if (!input || !input.value.trim()) return;
      const query = input.value.trim();

      try {
        const response = await fetch(`/api/v1/patients/search?query=${encodeURIComponent(query)}`);
        const results = await response.json();
        displayResults(element, results);
        loadDashboardData(element);
      } catch (error) {
        console.error("Fehler bei der Suche:", error);
      }
    };

    if (btn) btn.addEventListener('click', performSearchAction);
    if (input) {
      input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          performSearchAction();
        }
      });
    }
  }
}

function displayResults(element, patients) {
  const container = element.querySelector("#search-results");
  if (!container) return;

  if (!patients || patients.length === 0) {
    container.innerHTML = `<div style="text-align: center; color: #64748b; padding: 20px;">Keine Patienten gefunden.</div>`;
    return;
  }

  container.innerHTML = "";

  patients.forEach(patient => {
    const row = document.createElement("div");
    row.className = "patient-row-item";
    row.innerHTML = `
      <div>
        <span style="font-weight: 600; font-size: 16px;">👤 Patient: ${patient.first_name || patient.name || 'Unbekannt'} ${patient.last_name || ''}</span>
        <div style="font-size: 14px; color: #64748b; margin-top: 4px;">ID: ${patient.id}</div>
      </div>
      <button style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: 600; cursor: pointer;">
        🚨 Notfall-Zugriff (Break the Glass)
      </button>
    `;

    row.onclick = async () => {
      const reason = prompt(`Bitte geben Sie den Grund für den Notfallzugriff ein:`);

      if (reason && reason.trim() !== "") {
        try {
          const response = await fetch('/api/v1/emergency-access', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ patient_id: patient.id, reason: reason })
          });

          if (response.ok) {
            let data;
            try {
              data = await response.json();
            } catch (jsonErr) {
              alert("Fehler: Das Backend hat kein gültiges JSON gesendet!");
              return;
            }

            try {
              const medical = data.medical_data || data;
              const p = { ...patient, ...medical };

              const gpPhone = p.gp_phone || '';
              const emergencyPhone = p.emergency_contact_phone || p.ermergency_contact_phone || p.emergency_phone || '';

              container.innerHTML = `
                <div style="border: 1px solid #e2e8f0; padding: 25px; margin-top: 20px; border-radius: 12px; background: #ffffff; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); text-align: left; color: #1e293b;">
                  <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #ef4444; padding-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 20px; color: #0f172a;">🚨 Freigeschaltete Notfallakte: ${p.first_name || p.name || 'Patient'} ${p.last_name || ''}</h3>
                    <span style="background: #fef2f2; color: #ef4444; font-weight: 700; padding: 4px 12px; border-radius: 9999px; font-size: 14px; border: 1px solid #fee2e2;">Zugriff Protokolliert</span>
                  </div>
                  
                  <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; color: #1e293b;">
                      <h4 style="margin: 0 0 10px 0; color: #475569; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Stammdaten</h4>
                      <p style="margin: 8px 0;"><strong>Name:</strong> ${p.first_name || p.name || 'Unbekannt'} ${p.last_name || ''}</p>
                      <p style="margin: 8px 0;"><strong>Patienten-ID:</strong> #${p.id}</p>
                      <p style="margin: 8px 0;">
  <strong>Geburtsdatum:</strong> ${p.birth_date || p.birthdate || p.date_of_birth || p.dob || 'Nicht angegeben'}
</p>
                      <p style="margin: 8px 0;"><strong>Blutgruppe:</strong> ${p.blood_type || p.bloodgroup || 'Unbekannt'}</p>
                    </div>
                    
                    <div style="background: #fff7ed; padding: 15px; border-radius: 8px; border: 1px solid #ffedd5; color: #1e293b;">
                      <h4 style="margin: 0 0 10px 0; color: #c2410c; font-size: 14px; text-transform: uppercase; letter-spacing: 0.05em;">Hausarzt & Notfallkontakt</h4>
                      <p style="margin: 8px 0 0 0;"><strong>Hausarzt:</strong> ${p.gp_name || 'Nicht hinterlegt'}</p>
                      ${gpPhone ? `<a href="tel:${gpPhone}" class="call-btn call-btn-blue">📞 Arzt anrufen (${gpPhone})</a>` : '<span style="font-size: 12px; color: #94a3b8;">Keine Nummer hinterlegt</span>'}
                      <hr style="border: 0; border-top: 1px solid #ffedd5; margin: 12px 0;">
                      <p style="margin: 0;"><strong>Notfallkontakt:</strong> ${p.emergency_contact || p.emergency_contact_name || 'Nicht hinterlegt'}</p>
                      ${emergencyPhone ? `<a href="tel:${emergencyPhone}" class="call-btn call-btn-red">📞 Kontakt anrufen (${emergencyPhone})</a>` : '<span style="font-size: 12px; color: #94a3b8;">Keine Nummer hinterlegt</span>'}
                    </div>
                  </div>

                  <div style="margin-bottom: 20px; background: #fef2f2; padding: 15px; border-radius: 8px; border: 1px solid #fee2e2;">
                    <h4 style="margin: 0 0 10px 0; color: #dc2626; font-size: 15px; font-weight: bold;">⚠️ Allergien & Unverträglichkeiten</h4>
                    <div style="color: #991b1b; font-weight: 600; white-space: pre-line;">${p.allergies || 'Keine bekannten Allergien'}</div>
                  </div>

                  <div style="margin-bottom: 20px; background: #f0fdf4; padding: 15px; border-radius: 8px; border: 1px solid #dcfce7;">
                    <h4 style="margin: 0 0 10px 0; color: #16a34a; font-size: 15px; font-weight: bold;">💊 Aktuelle Medikation</h4>
                    <div style="color: #166534; white-space: pre-line;">${p.medications || 'Keine Dauermedikation'}</div>
                  </div>

                  <div style="background: #f0fdfa; padding: 15px; border-radius: 8px; border: 1px solid #ccfbf1;">
                    <h4 style="margin: 0 0 10px 0; color: #0d9488; font-size: 15px; font-weight: bold;">📋 Relevante Diagnosen / Vorerkrankungen</h4>
<div style="color: #115e59; white-space: pre-line;">
  ${
    (() => {
      // 1. Hole die Daten, egal ob conditions oder condition_list oder vorerkrankungen
      const data = p.conditions || p.condition_list || p.diagnoses;
      
      // 2. Wenn nichts da ist, zeige den Standardtext
      if (!data) return 'Keine chronischen Vorerkrankungen';
      
      // 3. Wenn es ein Array (Liste) ist, verbinde die Elemente mit Komma oder Zeilenumbruch
      if (Array.isArray(data)) {
        return data.length > 0 ? data.join(', ') : 'Keine chronischen Vorerkrankungen';
      }
      
      // 4. Wenn es bereits ein String ist, gib ihn einfach aus
      return data;
    })()
  }
</div>
                  <button onclick="location.reload()" style="margin-top: 20px; background: #64748b; color: white; border: none; padding: 10px 20px; border-radius: 6px; font-weight: 600; cursor: pointer;">
                    Zurück zur Suche
                  </button>
                </div>
              `;
            } catch (renderErr) {
              alert("HTML-Rendern fehlgeschlagen: " + renderErr.message);
            }
            loadDashboardData(element);
          } else {
            alert("Backend antwortete mit Fehler-Status: " + response.status);
          }
        } catch (error) {
          console.error("Verbindungsfehler:", error);
          alert("Server-Verbindungsfehler beim Abrufen der Akte.");
        }
      }
    };
    container.appendChild(row);
  });
}

async function loadDashboardData(element) {
  try {
    const response = await fetch('/api/v1/dashboard/data', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    if (!response.ok) throw new Error("Fehler beim Laden");
    const data = await response.json();

    const patientCountEl = element.querySelector('#patient-count');
    if (patientCountEl) patientCountEl.innerText = data.total_patients;

    const listEl = element.querySelector('#access-list');
    if (listEl && data.recent_access) {
      listEl.innerHTML = data.recent_access.map(acc => `
        <li style="color: #1e293b;">${acc.patient_name} - ${new Date(acc.time).toLocaleString()}</li>
      `).join('');
    }
  } catch (error) {
    console.error(error);
  }
}

async function loadVisualAnalytics(element) {
  try {
    const response = await fetch('/api/v1/dashboard/stats', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    if (!response.ok) throw new Error("Fehler beim Laden der Visualisierungen");
    const data = await response.json();

    const totalPatients = data.summary.total_patients || 1;

    const patientCountEl = element.querySelector('#patient-count');
    if (patientCountEl) {
      patientCountEl.innerHTML = `<strong style="color: #1e293b;">${totalPatients}</strong> <span style="font-size: 12px; color: #64748b; margin-left: 8px;">(🔓 ${data.summary.access_enabled} Aktiv / 🔒 ${data.summary.access_disabled} Inaktiv)</span>`;
    }

    const allergiesList = element.querySelector('#analytics-allergies-list');
    if (allergiesList && data.top_allergies) {
      if (data.top_allergies.length === 0) {
        allergiesList.innerHTML = `<p style="color: #64748b; font-size: 14px;">Keine Allergiedaten vorhanden.</p>`;
      } else {
        allergiesList.innerHTML = data.top_allergies.map(allergy => {
          const pct = ((allergy.count / totalPatients) * 100).toFixed(0);
          return `
            <div style="margin-bottom: 12px;">
              <div class="stats-flex-row">
                <span style="font-weight: 500; color: #1e293b;">${allergy.name}</span>
                <span style="color: #64748b;">${allergy.count} Pat. (${pct}%)</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${pct}%; background-color: #ef4444;"></div>
              </div>
            </div>
          `;
        }).join('');
      }
    }

    const conditionsList = element.querySelector('#analytics-conditions-list');
    if (conditionsList && data.top_conditions) {
      if (data.top_conditions.length === 0) {
        conditionsList.innerHTML = `<p style="color: #64748b; font-size: 14px;">Keine Diagnosen vorhanden.</p>`;
      } else {
        conditionsList.innerHTML = data.top_conditions.map(cond => {
          const pct = ((cond.count / totalPatients) * 100).toFixed(0);
          return `
            <div style="margin-bottom: 12px;">
              <div class="stats-flex-row">
                <span style="font-weight: 500; color: #1e293b;">${cond.name}</span>
                <span style="color: #64748b;">${cond.count} Pat. (${pct}%)</span>
              </div>
              <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: ${pct}%; background-color: #0284c7;"></div>
              </div>
            </div>
          `;
        }).join('');
      }
    }
  } catch (error) {
    console.error("Fehler beim Laden der Dashboard-Statistiken:", error);
  }
}

async function checkSystemStatus(element) {
  try {
    const response = await fetch('/api/v1/health')
    const data = await response.json()
    const statusDiv = element.querySelector('#system-status')
    if (statusDiv) {
      statusDiv.innerHTML = `
        <div class="status-item" style="color: #1e293b; margin-bottom: 5px;"><span>API Status: </span><span class="badge badge-success" style="background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px;">🟢 ${data.status}</span></div>
        <div class="status-item" style="color: #1e293b;"><span>Database: </span><span class="badge badge-success" style="background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px;">🟢 Verbunden</span></div>
      `
    }
  } catch (error) {
    console.error("System-Status-Check fehlgeschlagen:", error);
  }
}
