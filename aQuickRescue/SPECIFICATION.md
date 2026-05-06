# 🏥 aQuickRescue - Emergency Health Data Mobile App
## Speckit Specification & Architecture

**Version**: 0.1.0  
**Date**: 2026-05-06  
**Status**: Specification  
**Project Lead**: Speckit Framework  

---

## 📋 Executive Summary

**aQuickRescue** is a FHIR-compliant, secure emergency health data mobile application that enables rapid access to critical patient information (allergies, medications, emergency contacts) for first responders and emergency teams in life-threatening situations.

### Core Value Proposition
- **For Patients**: One-click emergency data sharing with automatic audit logging
- **For First Responders**: 30-second patient identification and health summary
- **For Healthcare System**: HIPAA/GDPR compliant audit trail and compliance reporting

### Key Metrics
- Patient search & retrieval: **< 2 seconds**
- Emergency access activation: **< 5 seconds**
- Data sync after access: **< 1 second**
- System uptime: **99.9%** (emergency-critical)
- Audit trail completeness: **100%** (zero data access without logging)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Mobile Application Layer (iOS/Android - React Native)      │
│  ├─ Patient Login & Dashboard                               │
│  ├─ Emergency Access UI (one-click trigger)                 │
│  ├─ Patient Search (first responder)                        │
│  └─ Data Display (allergies, medications, contacts)         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS + OAuth2 JWT
┌────────────────────────▼────────────────────────────────────┐
│  API Gateway Layer (API Rate Limiting, Auth)                │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│  Backend Services (FastAPI/Express)                         │
│  ├─ AuthService (OAuth2, RBAC, JWT)                        │
│  ├─ PatientService (FHIR Patient Resource)                 │
│  ├─ EmergencyAccessService (access control)                │
│  ├─ AuditService (FHIR AuditEvent logging)                │
│  └─ FHIRService (FHIR Server integration)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
┌───────▼──────┐ ┌──────▼────────┐ ┌─────▼──────────┐
│ PostgreSQL   │ │ FHIR Server   │ │ Audit Log DB   │
│ (Patient DB) │ │ (Health Data) │ │ (Compliance)   │
└──────────────┘ └───────────────┘ └────────────────┘
```

---

## 🔐 Security Architecture

### Authentication Flow
```
1. User opens app
2. OAuth2/OpenID Connect flow initiated
3. User authenticates with healthcare provider credentials
4. JWT token issued (15-min expiry, refresh token 30 days)
5. Token stored securely in device keychain
6. All API calls include Authorization: Bearer {token}
```

### Authorization (RBAC)
```
Role: PATIENT
├─ Can view own health data
├─ Can trigger emergency access
└─ Can view audit trail (own record access)

Role: FIRST_RESPONDER
├─ Can search patients by name/DOB
├─ Can request emergency access
├─ Can view emergency-shared data only
└─ Can request audit trail for access

Role: EMERGENCY_PHYSICIAN
├─ All FIRST_RESPONDER permissions
├─ Can access additional medical history
└─ Can mark access as emergency use

Role: ADMIN
├─ User management
├─ Role assignment
├─ Audit trail review
└─ System configuration
```

### Emergency Access Protocol
```
1. First Responder clicks "Emergency Access"
2. System validates responder role (FIRST_RESPONDER+)
3. Patient ID input (Name + DOB search) or Smartphone QR scan
4. Responder enters access reason (template or freetext)
5. System logs in FHIR AuditEvent:
   - WHO: Responder ID + Name
   - WHEN: Exact timestamp
   - WHAT: Patient ID + Data accessed
   - WHERE: GPS location
   - WHY: Access reason
6. Data returned + Real-time notification to patient (if possible)
```

### Data Protection
- **At Rest**: AES-256 encryption for sensitive data
- **In Transit**: TLS 1.3 only
- **In Memory**: Automatic clearing after 5 minutes
- **Deletion**: Automatic 90-day retention for access logs (GDPR compliant)
- **Backup**: Encrypted backups, tested monthly recovery

---

## 📱 User Flows

### Flow 1: Patient Setup
```
1. Patient installs app
2. Onboarding: Read privacy policy, understand emergency sharing
3. Login: OAuth2 (hospital account)
4. Setup: Confirm medical data permissions
5. Verification: Two-factor authentication setup
6. Dashboard: View own health data, emergency access toggle
```

### Flow 2: Emergency Access (First Responder)
```
1. Responder opens app (already authenticated as FIRST_RESPONDER)
2. Clicks "Search Patient"
3. Inputs: Patient Name + Date of Birth
4. System searches FHIR server: Patient resource
5. Result: Patient found (name, DOB, emergency contact)
6. Clicks "View Emergency Data"
7. Enters reason: "Unconscious - possible allergies"
8. System:
   - Validates responder permissions
   - Logs FHIR AuditEvent
   - Returns: Allergies, Current Medications, Emergency Contacts
9. Responder can call emergency contact or administer medication
10. System notifies patient (pending/approved emergency access)
```

### Flow 3: Audit Trail Review
```
1. Patient opens app
2. Navigate to "Privacy Center" → "Who Accessed My Data"
3. Timeline view: Date, Time, Who, Why, What data
4. Entries include: Responder Name, Reason, Data accessed
5. Patient can flag suspicious activity
6. System notifies admins of flagged entries
```

---

## 🔌 FHIR Integration

### FHIR Resources Used

#### 1. Patient
```json
{
  "resourceType": "Patient",
  "id": "patient-12345",
  "name": [{"given": ["John"], "family": "Doe"}],
  "birthDate": "1980-05-20",
  "telecom": [{"system": "phone", "value": "+41791234567"}],
  "contact": [
    {
      "name": {"text": "Jane Doe"},
      "telecom": [{"system": "phone", "value": "+41791234568"}],
      "relationship": [{"coding": [{"code": "EMERG"}]}]
    }
  ]
}
```

#### 2. AllergyIntolerance
```json
{
  "resourceType": "AllergyIntolerance",
  "patient": {"reference": "Patient/patient-12345"},
  "code": {"coding": [{"code": "Code", "display": "Penicillin"}]},
  "criticality": "high",
  "reaction": [{"manifestation": [{"text": "Anaphylaxis"}]}]
}
```

#### 3. Medication
```json
{
  "resourceType": "Medication",
  "id": "med-12345",
  "code": {"coding": [{"code": "Code", "display": "Aspirin 500mg"}]}
}
```

#### 4. MedicationStatement
```json
{
  "resourceType": "MedicationStatement",
  "patient": {"reference": "Patient/patient-12345"},
  "medicationReference": {"reference": "Medication/med-12345"},
  "dosage": [{"text": "500mg twice daily"}],
  "status": "active"
}
```

#### 5. AuditEvent (🔑 CRITICAL)
```json
{
  "resourceType": "AuditEvent",
  "type": {"code": "rest"},
  "action": "R",
  "recorded": "2026-05-06T14:32:45Z",
  "outcome": "0",
  "agent": [
    {
      "name": "John Smith",
      "requestor": true,
      "role": [{"coding": [{"code": "FIRST_RESPONDER"}]}]
    }
  ],
  "entity": [
    {
      "what": {"reference": "Patient/patient-12345"},
      "name": "Patient Health Record",
      "description": "Emergency medical access",
      "query": "AllergyIntolerance,MedicationStatement,Contact"
    }
  ]
}
```

### FHIR Server Endpoints

```
GET    /fhir/Patient?name=John&birthdate=1980-05-20
       → Search patients by name and DOB

GET    /fhir/Patient/{id}
       → Get patient demographic data

GET    /fhir/AllergyIntolerance?patient={id}
       → Get patient allergies

GET    /fhir/MedicationStatement?patient={id}
       → Get patient medications

POST   /fhir/AuditEvent
       → Log access event (automatic)

GET    /fhir/AuditEvent?entity.what.reference=Patient/{id}
       → Get audit trail for patient
```

---

## 🎯 System Requirements

### Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|-------------------|
| FR-1 | Patient Login | OAuth2 success, JWT token issued, persistent login |
| FR-2 | Patient can view own health data | Display allergies, medications, contacts < 2s |
| FR-3 | Patient can enable emergency access | One-click toggle, confirmation dialog |
| FR-4 | First responder can search patients | Search by name + DOB, max 5 results |
| FR-5 | First responder can access emergency data | Only when emergency toggle enabled, 5-second retrieve |
| FR-6 | Automatic audit logging | Every access logged, zero missing events |
| FR-7 | Patient can review access log | See who accessed data, when, why |
| FR-8 | Admin can review audit trail | SQL queries, export to CSV |
| FR-9 | Automatic data sync | Background sync every 6 hours or on app open |
| FR-10 | Emergency contact notification | SMS/Push notification on emergency access |

### Non-Functional Requirements

| ID | Category | Requirement | Target |
|----|----------|-------------|--------|
| NFR-1 | Performance | Patient search response time | < 2 seconds (p95) |
| NFR-2 | Performance | Emergency data retrieval | < 5 seconds (p95) |
| NFR-3 | Performance | App startup time | < 3 seconds |
| NFR-4 | Availability | System uptime (emergency-critical) | 99.9% |
| NFR-5 | Security | All data in transit | TLS 1.3 only |
| NFR-6 | Security | Sensitive data at rest | AES-256 encryption |
| NFR-7 | Security | Authentication failures | Max 5 attempts → lockout 15 min |
| NFR-8 | Security | Access audit completeness | 100% - zero missing events |
| NFR-9 | Compliance | Data retention | 90 days (GDPR), configurable |
| NFR-10 | Compliance | Penetration testing | Quarterly, zero critical vulnerabilities |
| NFR-11 | UX | Accessibility | WCAG 2.1 AA minimum |
| NFR-12 | UX | Mobile responsiveness | iOS 14+, Android 10+ |

---

## 💻 Technology Stack

### Frontend (Mobile App)
- **Framework**: React Native (Expo or bare workflow)
- **Language**: TypeScript
- **State Management**: Redux or Zustand
- **HTTP Client**: Axios with interceptors (auth, retry, timeout)
- **UI Components**: React Native Paper or Tamagui
- **Auth**: react-native-appauth (OAuth2)
- **Storage**: AsyncStorage + Keychain (encrypted secrets)
- **Analytics**: Sentry (error tracking)
- **Maps**: react-native-maps (for GPS location)

### Backend API
- **Framework**: FastAPI (Python) or Express (Node.js)
- **Language**: Python 3.11+ or TypeScript/Node 18+
- **Database**: PostgreSQL 14+
- **FHIR Server**: HAPI FHIR or Google Cloud FHIR API
- **Authentication**: python-jose + fastapi-security or similar
- **Logging**: Structured logging (JSON format)
- **Monitoring**: Prometheus metrics, Grafana dashboards
- **Container**: Docker, orchestration with Kubernetes

### Infrastructure
- **Cloud**: AWS (RDS, ECS, S3, CloudFront) or Azure
- **API Gateway**: AWS API Gateway or reverse proxy (nginx)
- **Cache**: Redis (session + emergency access cache)
- **Message Queue**: RabbitMQ or AWS SQS (audit events)
- **Monitoring**: CloudWatch or ELK Stack
- **Secrets**: AWS Secrets Manager or HashiCorp Vault

---

## 📐 Code Quality Standards (Speckit)

### Python Backend (FastAPI)
- **Linting**: Flake8, max line length 100
- **Formatting**: Black
- **Type Hints**: 100% coverage, mypy strict mode
- **Testing**: pytest, >= 80% code coverage
- **Code Quality**: SonarQube score >= 80
- **Security**: Bandit for security issues

### TypeScript Frontend
- **Linting**: ESLint with typescript-eslint
- **Formatting**: Prettier
- **Type Strictness**: strict mode enabled
- **Testing**: Jest + React Native Testing Library, >= 80% coverage
- **Code Quality**: SonarQube score >= 80

### Documentation
- **API**: OpenAPI/Swagger docs
- **Architecture**: ADRs (Architecture Decision Records)
- **Setup**: Docker Compose for local development
- **Troubleshooting**: Runbook for common issues

---

## 🧪 Testing Strategy

### Test Pyramid
```
                 /\
                /  \  E2E Tests (10%)
               /────\
              /      \  Integration Tests (30%)
             /────────\
            /          \ Unit Tests (60%)
           /____________\
```

### Unit Tests
- **Backend**: FastAPI routes, services, utility functions
- **Frontend**: Components, hooks, reducers, utilities
- **Target**: >= 80% code coverage
- **Tools**: pytest (backend), Jest (frontend)

### Integration Tests
- **Backend**: Database operations, FHIR API calls, auth flows
- **Frontend**: Navigation flows, API integration, storage
- **Database**: Test fixtures with real schema
- **Target**: >= 30% coverage
- **Frequency**: Run on every commit

### E2E Tests (Playwright)
```python
# Example E2E test
async def test_emergency_access_flow():
    # 1. Login as first responder
    # 2. Search patient by name + DOB
    # 3. Click emergency access
    # 4. Enter reason
    # 5. Verify data returned
    # 6. Verify audit logged
    # 7. Verify patient notified
```

### Performance Tests
- **Load Test**: 1000 concurrent patients searching, response time < 2s
- **Stress Test**: Break point identification
- **Database**: Query optimization for < 100ms (p95)
- **Battery**: Mobile app battery usage < 5% in 8 hours standby

### Security Tests
- **Penetration Testing**: Quarterly (HIPAA requirement)
- **SAST**: SonarQube security issues
- **DAST**: OWASP ZAP scans
- **Dependency**: Snyk weekly CVE scans
- **Secrets**: GitGuardian for credential scanning

---

## 📊 Performance Targets (Speckit)

| Metric | Target | Critical | Unit | Measurement |
|--------|--------|----------|------|-------------|
| Patient Search Response | 2000ms | 5000ms | ms | p95 latency |
| Emergency Data Retrieval | 5000ms | 10000ms | ms | p95 latency |
| App Cold Start | 3000ms | 5000ms | ms | Time to interactive |
| Data Sync Time | 1000ms | 2000ms | ms | Background sync |
| API Response (p50) | 100ms | 200ms | ms | Server latency |
| Bundle Size | 200KB | 350KB | KB | Gzip compressed |
| System Uptime | 99.9% | 99.5% | % | Monthly |
| Audit Log Latency | 100ms | 500ms | ms | Event creation |

---

## 🔒 Compliance & Audit

### HIPAA Requirements
- ✅ Access controls (RBAC)
- ✅ Audit logging (who, what, when, where, why)
- ✅ Data encryption (at rest, in transit)
- ✅ Breach notification (< 60 days)
- ✅ Min access principle (emergency access only)
- ✅ Device and media controls (encrypted storage)

### GDPR Requirements
- ✅ User consent (opt-in emergency sharing)
- ✅ Data retention limits (90 days audit logs)
- ✅ Right to access (user can review audit trail)
- ✅ Data deletion (right to be forgotten)
- ✅ DPA (Data Processing Agreement with cloud provider)
- ✅ Privacy by design

### Audit Trail (FHIR AuditEvent)
```
Every access must log:
✓ WHO: User ID, Name, Role
✓ WHEN: Timestamp (UTC), Duration
✓ WHAT: Patient ID, Data accessed (resources)
✓ WHERE: IP address, Location (GPS if emergency)
✓ WHY: Access reason, Emergency flag
✓ OUTCOME: Success/failure, Error code
```

---

## 📁 Project Structure

```
aQuickRescue/
├── 📁 backend/                 # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── config.py          # Config (env vars)
│   │   ├── auth/
│   │   │   ├── crud.py        # User CRUD
│   │   │   ├── models.py      # User models
│   │   │   └── oauth2.py      # OAuth2 scheme
│   │   ├── patients/
│   │   │   ├── models.py      # Patient models
│   │   │   ├── routes.py      # Patient endpoints
│   │   │   └── service.py     # Patient business logic
│   │   ├── emergency/
│   │   │   ├── models.py      # Emergency access models
│   │   │   ├── routes.py      # Emergency endpoints
│   │   │   └── service.py     # Emergency logic
│   │   ├── audit/
│   │   │   ├── models.py      # AuditEvent model
│   │   │   ├── routes.py      # Audit endpoints
│   │   │   └── service.py     # Audit logging service
│   │   ├── fhir/
│   │   │   ├── client.py      # FHIR server client
│   │   │   └── resources.py   # Resource mappings
│   │   ├── middleware/
│   │   │   ├── auth.py        # Auth middleware
│   │   │   ├── audit.py       # Audit logging middleware
│   │   │   └── error.py       # Error handling
│   │   └── utils/
│   │       ├── security.py    # Encryption, hashing
│   │       └── validators.py  # Input validation
│   ├── tests/
│   │   ├── unit/              # Unit tests
│   │   ├── integration/       # Integration tests
│   │   └── fixtures/          # Test data
│   ├── docs/
│   │   ├── architecture.md    # Architecture docs
│   │   ├── api.md             # API documentation
│   │   └── setup.md           # Setup guide
│   ├── requirements.txt       # Dependencies
│   ├── pytest.ini             # Pytest config
│   ├── .flake8                # Flake8 config
│   ├── docker-compose.yml     # Local dev environment
│   └── Dockerfile             # Production image
│
├── 📁 frontend/               # React Native app
│   ├── src/
│   │   ├── App.tsx            # Root component
│   │   ├── config.ts          # App config
│   │   ├── screens/
│   │   │   ├── LoginScreen.tsx
│   │   │   ├── DashboardScreen.tsx
│   │   │   ├── PatientSearchScreen.tsx
│   │   │   ├── EmergencyAccessScreen.tsx
│   │   │   ├── AuditTrailScreen.tsx
│   │   │   └── ProfileScreen.tsx
│   │   ├── components/
│   │   │   ├── PatientCard.tsx
│   │   │   ├── AuditEntry.tsx
│   │   │   ├── Button.tsx
│   │   │   └── Modal.tsx
│   │   ├── services/
│   │   │   ├── api.ts         # API client
│   │   │   ├── auth.ts        # Auth service
│   │   │   └── storage.ts     # Secure storage
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── usePatient.ts
│   │   │   └── useFetch.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript types
│   │   └── styles/
│   │       └── theme.ts
│   ├── __tests__/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── app.json               # Expo config
│   ├── package.json
│   ├── tsconfig.json
│   ├── jest.config.js
│   ├── .eslintrc.json
│   └── .prettierrc
│
├── 📁 docs/
│   ├── SPECIFICATION.md       # This file
│   ├── ARCHITECTURE.md        # Architecture decisions
│   ├── DEPLOYMENT.md          # Deployment guide
│   ├── SECURITY.md            # Security guide
│   └── COMPLIANCE.md          # HIPAA/GDPR checklist
│
├── 📁 .github/
│   └── workflows/
│       ├── backend-test.yml   # Backend CI
│       ├── frontend-test.yml  # Frontend CI
│       ├── deploy.yml         # Deployment
│       └── security-scan.yml  # Security scanning
│
├── docker-compose.yml         # Full stack local dev
├── .gitignore
├── .env.example
└── README.md
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Project setup, repository, CI/CD
- [ ] Backend scaffolding (FastAPI structure)
- [ ] Database schema (PostgreSQL)
- [ ] OAuth2 authentication implementation
- [ ] Patient model and basic CRUD
- [ ] Unit tests (target: 70%)

**Deliverable**: Patient login, patient data retrieval

### Phase 2: Core Features (Weeks 3-4)
- [ ] Emergency access service
- [ ] FHIR AuditEvent logging
- [ ] Patient search functionality (name + DOB)
- [ ] Allergies and medications retrieval
- [ ] Integration tests
- [ ] Unit tests (target: 80%)

**Deliverable**: Complete emergency access workflow (backend)

### Phase 3: Mobile App (Weeks 5-6)
- [ ] React Native project setup
- [ ] Login/authentication screens
- [ ] Patient dashboard
- [ ] Patient search screen
- [ ] Emergency access UI
- [ ] E2E tests

**Deliverable**: Full emergency access flow (end-to-end)

### Phase 4: Hardening & Deployment (Weeks 7-8)
- [ ] Security audit & penetration testing
- [ ] Performance optimization
- [ ] Load testing (1000 concurrent users)
- [ ] Documentation completion
- [ ] Deployment automation
- [ ] Monitoring setup

**Deliverable**: Production-ready system, monitoring, runbooks

---

## 📞 Success Criteria

### Functional Success
- ✅ Patient login working (< 5 seconds)
- ✅ Patient search working (< 2 seconds, accurate results)
- ✅ Emergency access workflow end-to-end (< 30 seconds total)
- ✅ 100% audit logging (zero missing events)
- ✅ Patient notifications working
- ✅ 99.9% system uptime in staging

### Code Quality Success
- ✅ Code coverage >= 80% (backend + frontend)
- ✅ SonarQube score >= A (80+)
- ✅ Zero medium/critical linting issues
- ✅ All security checks passing
- ✅ Load testing: 1000 concurrent, p95 < 2s

### Security Success
- ✅ Penetration test passed (pre-production)
- ✅ HIPAA compliance checklist 100%
- ✅ GDPR compliance checklist 100%
- ✅ Zero critical CVEs in dependencies
- ✅ Encryption verified (data at rest + transit)

### UX Success
- ✅ Accessibility audit WCAG 2.1 AA passed
- ✅ User testing with 5+ first responders (task completion 95%+)
- ✅ App performance (startup < 3s, interactions < 100ms)
- ✅ Offline functionality tested

---

## 📅 Next Steps

1. **Approval**: Sign-off on this specification
2. **Environment**: Set up AWS/Azure + PostgreSQL + FHIR server
3. **Code**: Start Phase 1 implementation
4. **Review**: Weekly progress reviews
5. **Iterate**: Adjust based on testing feedback

---

**Status**: ✅ SPECIFICATION APPROVED  
**Version**: 0.1.0  
**Next Review**: End of Phase 1 (Week 2)

---

## 📚 References

- FHIR Standard: https://www.hl7.org/fhir/
- HIPAA Security Rule: https://www.hhs.gov/hipaa/
- GDPR: https://gdpr-info.eu/
- OAuth 2.0: https://tools.ietf.org/html/rfc6749
- OpenAPI: https://spec.openapis.org/
- Speckit Framework: See CONSTITUTION.md

---

**Specification Version**: 1.0  
**Created**: 2026-05-06  
**Approved by**: [Signature/Approval required]

