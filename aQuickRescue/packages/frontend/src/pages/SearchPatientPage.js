/**
 * Patient Search Page
 */

import { patientAPI } from '../services/api.js'
import { store, searchSelectors } from '../state/store.js'
import { validatePatientSearch } from '../utils/validators.js'
import { handleError } from '../utils/logging.js'

export const createSearchPage = {
  render() {
    const results = store.getState().searchResults
    const loading = store.getState().loading

    return `
      <div class="container search-container">
        <div class="search-header">
          <h1>🔍 Patient suchen</h1>
          <p>Patient nach Namen und Geburtsdatum suchen</p>
        </div>

        <div class="search-form-card">
          <form id="search-form" class="search-form">
            <div class="form-row">
              <div class="form-group">
                <label for="first-name">Vorname</label>
                <input
                  type="text"
                  id="first-name"
                  name="first_name"
                  placeholder="z.B. Max"
                  required
                />
                <span class="error-message" data-error="first_name"></span>
              </div>

              <div class="form-group">
                <label for="last-name">Nachname</label>
                <input
                  type="text"
                  id="last-name"
                  name="last_name"
                  placeholder="z.B. Mustermann"
                  required
                />
                <span class="error-message" data-error="last_name"></span>
              </div>

              <div class="form-group">
                <label for="dob">Geburtsdatum</label>
                <input
                  type="date"
                  id="dob"
                  name="date_of_birth"
                  required
                />
                <span class="error-message" data-error="date_of_birth"></span>
              </div>
            </div>

            <button
              type="submit"
              class="btn btn-primary"
              id="search-btn"
              ${loading ? 'disabled' : ''}
            >
              ${loading ? '🔄 Suche läuft...' : '🔍 Suchen'}
            </button>
          </form>

          <div id="alert" class="alert" style="display: none;"></div>
        </div>

        <div class="search-results">
          ${results.length > 0 ? `
            <div class="results-header">
              <h2>Suchergebnisse (${results.length})</h2>
            </div>

            <div class="results-list">
              ${results.map((patient, index) => `
                <div class="result-card" data-patient-id="${patient.id}">
                  <div class="result-info">
                    <h3>${patient.name}</h3>
                    <p><strong>Geb. Datum:</strong> ${patient.birthDate}</p>
                    <p><strong>Patient-ID:</strong> <code>${patient.id}</code></p>
                  </div>
                  <div class="result-actions">
                    <button class="btn btn-sm btn-primary select-patient-btn">
                      Auswählen
                    </button>
                  </div>
                </div>
              `).join('')}
            </div>
          ` : ''}

          ${!loading && results.length === 0 && store.getState().searchResults.length === 0 ? `
            <div class="empty-state">
              <p>Geben Sie die Patientendaten ein und klicken Sie auf "Suchen"</p>
            </div>
          ` : ''}

          ${!loading && results.length === 0 && store.getState().searchResults.length > 0 ? `
            <div class="empty-state error">
              <p>Keine Patienten gefunden</p>
            </div>
          ` : ''}
        </div>
      </div>
    `
  },

  attachListeners(element) {
    const form = element.querySelector('#search-form')
    const alert = element.querySelector('#alert')
    const searchBtn = element.querySelector('#search-btn')

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()

        const formData = {
          first_name: form.querySelector('#first-name').value.trim(),
          last_name: form.querySelector('#last-name').value.trim(),
          date_of_birth: form.querySelector('#dob').value
        }

        // Validate
        const validation = validatePatientSearch(formData)
        if (!validation.isValid) {
          Object.entries(validation.errors).forEach(([field, message]) => {
            const errorSpan = element.querySelector(`[data-error="${field}"]`)
            if (errorSpan) {
              errorSpan.textContent = message
            }
          })
          return
        }

        // Clear errors
        element.querySelectorAll('.error-message').forEach((span) => {
          span.textContent = ''
        })

        try {
          alert.style.display = 'none'
          await patientAPI.search(
            formData.first_name,
            formData.last_name,
            formData.date_of_birth
          )
        } catch (error) {
          handleError(error, 'Patient Search')
          alert.style.display = 'flex'
          alert.className = 'alert alert-danger'
          alert.innerHTML = `
            <span>❌ Suche fehlgeschlagen: ${error.response?.data?.detail || error.message}</span>
            <button class="alert-close" type="button">&times;</button>
          `

          element.querySelector('.alert-close')?.addEventListener('click', () => {
            alert.style.display = 'none'
          })
        }
      })
    }

    // Select patient buttons
    const selectBtns = element.querySelectorAll('.select-patient-btn')
    selectBtns.forEach((btn) => {
      btn.addEventListener('click', (e) => {
        const card = e.target.closest('.result-card')
        const patientId = card.getAttribute('data-patient-id')
        const patient = store.getState().searchResults.find((p) => p.id === patientId)

        store.getState().setSelectedPatient(patient)
        window.location.href = '/emergency-access'
      })
    })
  }
}

