/**
 * Emergency Access Page
 */

import { emergencyAPI } from '../services/api.js'
import { store } from '../state/store.js'
import { validateEmergencyAccessRequest } from '../utils/validators.js'
import { handleError } from '../utils/logging.js'
import { formatDate, formatStatus } from '../utils/formatters.js'

export const createEmergencyAccessPage = {
  render() {
    const selectedPatient = store.getState().selectedPatient
    const currentAccess = store.getState().currentEmergencyAccess
    const loading = store.getState().loading

    return `
      <div class="container emergency-container">
        <div class="emergency-header">
          <h1>🚨 Notfallzugriff anfordern</h1>
          <p>Zugriff auf wichtige Patientendaten im Notfall</p>
        </div>

        ${!currentAccess ? `
          <div class="emergency-form-card">
            <form id="emergency-form" class="emergency-form">
              <div class="form-section">
                <h2>Patient-Informationen</h2>

                ${selectedPatient ? `
                  <div class="info-box">
                    <p><strong>Patient:</strong> ${selectedPatient.name}</p>
                    <p><strong>Geb. Datum:</strong> ${selectedPatient.birthDate}</p>
                    <p><strong>Patient-ID:</strong> <code>${selectedPatient.id}</code></p>
                  </div>
                ` : `
                  <div class="form-group">
                    <label for="patient-id">Patient-ID</label>
                    <input
                      type="text"
                      id="patient-id"
                      name="patient_id"
                      placeholder="Patient-ID eingeben oder suchen"
                      required
                    />
                    <span class="error-message" data-error="patient_id"></span>
                    <a href="/search" class="btn btn-sm btn-secondary" style="margin-top: 8px;">
                      🔍 Patient suchen
                    </a>
                  </div>
                `}
              </div>

              <div class="form-section">
                <h2>Grund des Zugriffs</h2>
                <div class="form-group">
                  <label for="reason">Grund (mind. 10 Zeichen)</label>
                  <textarea
                    id="reason"
                    name="reason"
                    placeholder="z.B. Patient bewusstlos, kritische Allergien prüfen"
                    rows="4"
                    required
                  ></textarea>
                  <span class="error-message" data-error="reason"></span>
                </div>
              </div>

              <div class="form-section">
                <h2>Angeforderte Daten</h2>
                <div class="form-group">
                  <label>Wählen Sie Datentypen aus:</label>
                  <div class="checkbox-group">
                    <label class="checkbox-label">
                      <input type="checkbox" name="requested_data" value="Allergies" required>
                      🚫 Allergien
                    </label>
                    <label class="checkbox-label">
                      <input type="checkbox" name="requested_data" value="Medications">
                      💊 Medikationen
                    </label>
                    <label class="checkbox-label">
                      <input type="checkbox" name="requested_data" value="Contacts">
                      📞 Kontakte
                    </label>
                    <label class="checkbox-label">
                      <input type="checkbox" name="requested_data" value="MedicalHistory">
                      📋 Medizinische Vorgeschichte
                    </label>
                  </div>
                  <span class="error-message" data-error="requested_data"></span>
                </div>
              </div>

              <div class="form-section">
                <h2>GPS-Standort</h2>
                <div class="form-group">
                  <label for="gps">GPS-Koordinaten (optional)</label>
                  <input
                    type="text"
                    id="gps"
                    name="gps_location"
                    placeholder="z.B. 52.5200,13.4050"
                  />
                  <button type="button" class="btn btn-sm btn-secondary" id="get-location-btn">
                    📍 Aktuellen Standort verwenden
                  </button>
                </div>
              </div>

              <div id="alert" class="alert" style="display: none;"></div>

              <button
                type="submit"
                class="btn btn-danger btn-large"
                id="request-btn"
                ${loading ? 'disabled' : ''}
              >
                ${loading ? '🔄 Wird verarbeitet...' : '🚨 Notfallzugriff anfordern'}
              </button>
            </form>
          </div>
        ` : `
          <div class="success-card">
            <div class="success-icon">✅</div>
            <h2>Zugriff erfolgreich gewährt</h2>

            <div class="access-details">
              <h3>Patient</h3>
              <p><strong>Name:</strong> ${currentAccess.patient.name}</p>
              <p><strong>Geb. Datum:</strong> ${currentAccess.patient.dob}</p>

              <h3>Notfallkontakt</h3>
              <p><strong>Name:</strong> ${currentAccess.emergency_contact.name}</p>
              <p><strong>Telefon:</strong> ${currentAccess.emergency_contact.phone}</p>

              <h3>🚫 Allergien</h3>
              ${currentAccess.allergies.length > 0 ? `
                <ul>
                  ${currentAccess.allergies.map((allergy) => `
                    <li>
                      <strong>${allergy.display}</strong>
                      (Kritikalität: ${allergy.criticality})
                    </li>
                  `).join('')}
                </ul>
              ` : '<p>Keine bekannten Allergien</p>'}

              <h3>💊 Medikationen</h3>
              ${currentAccess.medications.length > 0 ? `
                <ul>
                  ${currentAccess.medications.map((med) => `
                    <li>
                      <strong>${med.medication}</strong><br>
                      Dosierung: ${med.dosage}
                    </li>
                  `).join('')}
                </ul>
              ` : '<p>Keine Medikationen bekannt</p>'}
            </div>

            <p class="timestamp">
              Zugriff gewährt: ${new Date(currentAccess.access_timestamp).toLocaleString('de-DE')}
            </p>

            <div class="action-buttons">
              <button class="btn btn-primary" onclick="window.location.href='/search'">
                🔍 Andere Patient suchen
              </button>
              <button class="btn btn-secondary" onclick="window.location.href='/dashboard'">
                📊 Zum Dashboard
              </button>
            </div>
          </div>
        `}
      </div>
    `
  },

  attachListeners(element) {
    const form = element.querySelector('#emergency-form')
    const alert = element.querySelector('#alert')
    const getLocationBtn = element.querySelector('#get-location-btn')

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()

        const selectedPatient = store.getState().selectedPatient
        const patientId = selectedPatient?.id || form.querySelector('#patient-id').value

        const checkboxes = form.querySelectorAll('input[name="requested_data"]:checked')
        const requestedData = Array.from(checkboxes).map((cb) => cb.value)

        const formData = {
          patient_id: patientId,
          reason: form.querySelector('#reason').value.trim(),
          requested_data: requestedData,
          gps_location: form.querySelector('#gps').value || null
        }

        // Validate
        const validation = validateEmergencyAccessRequest(formData)
        if (!validation.isValid) {
          Object.entries(validation.errors).forEach(([field, message]) => {
            const errorSpan = element.querySelector(`[data-error="${field}"]`)
            if (errorSpan) {
              errorSpan.textContent = message
            }
          })
          return
        }

        try {
          alert.style.display = 'none'
          await emergencyAPI.requestAccess(
            formData.patient_id,
            formData.reason,
            formData.requested_data,
            formData.gps_location
          )
          // The page will re-render showing the success state
        } catch (error) {
          handleError(error, 'Emergency Access')
          alert.style.display = 'flex'
          alert.className = 'alert alert-danger'
          alert.innerHTML = `
            <span>❌ Zugriff fehlgeschlagen: ${error.response?.data?.detail || error.message}</span>
            <button class="alert-close" type="button">&times;</button>
          `
        }
      })
    }

    if (getLocationBtn) {
      getLocationBtn.addEventListener('click', (e) => {
        e.preventDefault()
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition((position) => {
            const gpsInput = element.querySelector('#gps')
            gpsInput.value = `${position.coords.latitude},${position.coords.longitude}`
          }, () => {
            alert('Standortzugriff verweigert')
          })
        }
      })
    }
  }
}

