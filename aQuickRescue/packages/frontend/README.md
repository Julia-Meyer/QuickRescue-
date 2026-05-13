# aQuickRescue Frontend

🚨 **Emergency Health Data Access Platform** - Vanilla JavaScript + Vite + SQLite

## Overview

aQuickRescue Frontend is a modern, lightweight web application for managing emergency health data access. Built with vanilla HTML, CSS, and JavaScript using Vite as the build tool.

### Features

- 🔍 **Patient Search** - Search for patients by name and date of birth
- 🚨 **Emergency Access** - Request quick access to critical patient data (allergies, medications, contacts)
- 📋 **Audit Trail** - View complete access history and maintain HIPAA compliance
- 🏥 **Health Data Management** - Access FHIR-compliant patient data
- 💾 **Local Storage** - SQLite database for offline metadata and images
- 🔐 **OAuth2 Authentication** - Secure JWT-based authentication
- 📱 **Responsive Design** - Mobile-first, works on all devices
- ♿ **Accessibility** - WCAG 2.1 AA compliant

## Tech Stack

- **Build Tool**: Vite 5
- **Language**: Vanilla JavaScript (ES2021+)
- **Styling**: Vanilla CSS with CSS Variables
- **State Management**: Zustand
- **Database**: SQLite + IndexedDB
- **HTTP Client**: Axios
- **Testing**: Vitest + Playwright

## Getting Started

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0

### Installation

```bash
# Install dependencies
npm install
npm install --workspace=packages/frontend

# Copy environment file
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

### Development

```bash
# Start development server
npm run dev --workspace=packages/frontend

# Development server runs on http://localhost:5173
```

### Building

```bash
# Build for production
npm run build --workspace=packages/frontend

# Output: packages/dist/
```

### Testing

```bash
# Run unit tests
npm test --workspace=packages/frontend

# Run tests with coverage
npm run test:coverage --workspace=packages/frontend

# Run E2E tests
npm run test:e2e --workspace=packages/frontend

# Run tests in UI mode
npm run test:ui --workspace=packages/frontend
```

### Code Quality

```bash
# Run linting
npm run lint --workspace=packages/frontend

# Fix linting issues
npm run lint:fix --workspace=packages/frontend

# Format code
npm run format --workspace=packages/frontend
```

## Project Structure

```
packages/frontend/
├── src/
│   ├── main.js                 # Entry point
│   ├── app.js                  # Main app component
│   ├── index.html              # HTML template
│   ├── components/             # Reusable components
│   │   ├── Header.js
│   │   └── Footer.js
│   ├── pages/                  # Page components
│   │   ├── LoginPage.js
│   │   ├── DashboardPage.js
│   │   ├── SearchPatientPage.js
│   │   ├── EmergencyAccessPage.js
│   │   ├── AuditTrailPage.js
│   │   └── NotFoundPage.js
│   ├── router/                 # Client-side routing
│   │   └── index.js
│   ├── services/               # Business logic services
│   │   ├── api.js              # Backend API client
│   │   ├── auth.js             # Authentication service
│   │   └── db.js               # SQLite database service
│   ├── state/                  # State management
│   │   └── store.js            # Zustand store
│   ├── styles/                 # CSS files
│   │   ├── main.css            # Base styles
│   │   ├── layout.css          # Layout components
│   │   ├── components.css      # Component styles
│   │   └── responsive.css      # Responsive design
│   └── utils/                  # Utility functions
│       ├── logging.js          # Logging utilities
│       ├── formatters.js       # Data formatting
│       └── validators.js       # Form validation
├── vite.config.js              # Vite configuration
├── package.json                # NPM dependencies
├── .eslintrc.json              # ESLint configuration
├── .prettierrc.json            # Prettier configuration
└── README.md                   # This file
```

## API Integration

The frontend communicates with the FastAPI backend at:

- **Base URL**: `http://localhost:8000` (configurable via `VITE_API_URL`)
- **API Version**: `/api/v1`
- **Authentication**: Bearer token (JWT)

### Key Endpoints

- `POST /auth/login` - User login
- `GET /patients/search` - Search patients
- `POST /emergency-access` - Request emergency access
- `GET /audit-trail` - Get audit trail
- `GET /health` - Health check

## Database (SQLite)

The frontend uses SQLite (via sql.js) for local metadata storage:

### Tables

- **metadata** - App configuration and sync state
- **patients** - Patient profiles (local cache)
- **images** - Patient images and documents
- **audit_cache** - Local audit events awaiting sync
- **cache_responses** - Cached API responses

### Persistence

Data is persisted to IndexedDB for browser compatibility and durability.

## State Management

Using Zustand for lightweight reactive state:

```javascript
import { store, authSelectors, searchSelectors } from './state/store.js'

// Get state
const { isAuthenticated, user } = store.getState()

// Set state
store.getState().setAuth(token, user)

// Subscribe to changes
const unsubscribe = store.subscribe(() => {
  console.log('State changed')
})
```

## Authentication Flow

1. User enters credentials on login page
2. Frontend sends credentials to backend
3. Backend validates and returns JWT token
4. Frontend stores token in localStorage
5. Token included in all subsequent API requests
6. On 401, token is refreshed or user redirected to login

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- iOS Safari 14+
- Chrome Mobile 90+

## Performance Targets (Speckit)

- Page Load: < 2 seconds
- Patient Search: < 2 seconds
- Emergency Access: < 5 seconds
- API Response: < 3 seconds
- Bundle Size: < 200KB (gzipped)

## Security

- ✅ No sensitive data in localStorage (tokens only)
- ✅ HTTPS only in production
- ✅ Content Security Policy headers
- ✅ CSRF protection via SameSite cookies
- ✅ Input validation and sanitization
- ✅ XSS prevention via DOM API (no innerHTML for user data)

## Accessibility

- ✅ WCAG 2.1 AA compliant
- ✅ Semantic HTML
- ✅ ARIA labels and roles
- ✅ Keyboard navigation support
- ✅ Screen reader compatible
- ✅ Color contrast > 4.5:1

## Development Tips

### Adding a New Page

1. Create file in `src/pages/NewPage.js`
2. Export `createNewPage` with `render()` and `attachListeners()` methods
3. Add route in `src/router/index.js`
4. Import route component in router file

### Adding a New API Endpoint

1. Add function in `src/services/api.js`
2. Use `apiClient` instance (includes auth headers)
3. Handle errors and update store state
4. Log actions via `logAction()`

### Styling Guidelines

- Use CSS variables (defined in `main.css`)
- Mobile-first responsive design
- BEM naming convention for classes
- No CSS framework - vanilla CSS only

## Debugging

Enable debug mode:

```javascript
// In console
localStorage.setItem('DEBUG', 'true')
location.reload()
```

View database:

```javascript
// In console
const db = await import('./services/db.js')
db.query('SELECT * FROM audit_cache')
```

## Troubleshooting

### API Not Responding

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Update VITE_API_URL if needed
# Edit .env.local
```

### Database Not Persisting

- IndexedDB may be disabled in private browsing
- Try clearing browser cache and reloading
- Check browser console for errors

### Login Fails

- Verify backend credentials are correct
- Check token format in localStorage
- Ensure CORS is configured on backend

## Contributing

See [CONTRIBUTING.md](../../docs/CONTRIBUTING.md)

## License

MIT License - See [LICENSE](../../LICENSE)

## Support

For issues and questions:
- 📧 Email: support@aQuickRescue.dev
- 🐛 Issues: https://github.com/yourusername/aQuickRescue/issues
- 💬 Discussions: https://github.com/yourusername/aQuickRescue/discussions

