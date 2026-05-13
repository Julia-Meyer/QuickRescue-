/**
 * Login Page
 */

import { authAPI } from '../services/api.js'
import { saveAuth } from '../services/auth.js'
import { store } from '../state/store.js'
import { validateLoginForm } from '../utils/validators.js'
import { handleError } from '../utils/logging.js'

export const createLoginPage = {
  render() {
    return `
      <div class="container">
        <div class="login-container">
          <div class="login-card">
            <h1>aQuickRescue</h1>
            <p class="subtitle">Notfalldatenverwaltung</p>

            <form id="login-form" class="login-form">
              <div class="form-group">
                <label for="username">Benutzername</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  placeholder="Benutzername eingeben"
                  required
                  autocomplete="username"
                />
                <span class="error-message" data-error="username"></span>
              </div>

              <div class="form-group">
                <label for="password">Passwort</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  placeholder="Passwort eingeben"
                  required
                  autocomplete="current-password"
                />
                <span class="error-message" data-error="password"></span>
              </div>

              <div id="alert" class="alert" style="display: none;"></div>

              <button type="submit" class="btn btn-primary btn-block" id="submit-btn">
                Anmelden
              </button>

              <div class="login-help">
                <p>Demo-Anmeldedaten:</p>
                <ul>
                  <li><strong>Ersthelfer:</strong> responder1 / password123</li>
                  <li><strong>Patient:</strong> patient1 / password123</li>
                  <li><strong>Admin:</strong> admin1 / password123</li>
                </ul>
              </div>
            </form>
          </div>
        </div>
      </div>
    `
  },

  attachListeners(element) {
    const form = element.querySelector('#login-form')
    const alert = element.querySelector('#alert')
    const submitBtn = element.querySelector('#submit-btn')

    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault()

        const formData = {
          username: form.querySelector('#username').value.trim(),
          password: form.querySelector('#password').value
        }

        // Validate
        const validation = validateLoginForm(formData)
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
          submitBtn.disabled = true
          submitBtn.textContent = 'Anmelden...'
          alert.style.display = 'none'

          const response = await authAPI.login(formData.username, formData.password)

          // Save auth
          saveAuth(response.access_token, response.user)
          store.getState().setAuth(response.access_token, response.user)

          // Redirect
          window.location.href = '/dashboard'
        } catch (error) {
          handleError(error, 'Login')
          alert.style.display = 'flex'
          alert.className = 'alert alert-danger'
          alert.innerHTML = `
            <span>❌ Anmeldung fehlgeschlagen: ${error.response?.data?.detail || error.message}</span>
            <button class="alert-close" type="button">&times;</button>
          `

          element.querySelector('.alert-close')?.addEventListener('click', () => {
            alert.style.display = 'none'
          })
        } finally {
          submitBtn.disabled = false
          submitBtn.textContent = 'Anmelden'
        }
      })
    }
  }
}

