# Mock.Health FHIR API Integration

## Overview

Das aQuickRescue Backend ist jetzt integriert mit der **Mock.Health FHIR API** für echte Healthcare-Daten.

## Konfiguration

Die Mock.Health Credentials sind bereits in `env/env.mockhealth` konfiguriert:

```bash
MOCK_HEALTH_API_KEY=sk_live_jyIdoD4ZWKc9ASt0TPs3DofEpPxOjrl6rH7mWWbHoRbo_IFoMx00neoILhLei-fi
MOCK_HEALTH_API_URL=https://api.mock.health
MOCK_HEALTH_FHIR_URL=https://api.mock.health/fhir
```

## Setup

### 1. Umgebung laden
```bash
# Kopiere env.mockhealth ins Projekt oder lade manually
export MOCK_HEALTH_API_KEY=$(grep MOCK_HEALTH_API_KEY env/env.mockhealth | cut -d= -f2)
export MOCK_HEALTH_API_URL=$(grep MOCK_HEALTH_API_URL env/env.mockhealth | cut -d= -f2)
export MOCK_HEALTH_FHIR_URL=$(grep MOCK_HEALTH_FHIR_URL env/env.mockhealth | cut -d= -f2)
```

### 2. Dependencies installieren
```bash
pip install -r aQuickRescue/backend/requirements.txt
```

### 3. Backend starten
```bash
cd aQuickRescue/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

Alle Endpoints erfordern Authentication (JWT Bearer Token) und sind für `FIRST_RESPONDER`, `EMERGENCY_PHYSICIAN`, oder `ADMIN` Rollen verfügbar.

### Patient Search & Retrieval

#### Search Patients
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/patients?given=John&family=Doe"
```

**Response:**
```json
{
  "found": true,
  "patients": [
    {
      "id": "123",
      "name": "John Doe",
      "birthDate": "1980-01-15"
    }
  ]
}
```

#### Get Single Patient
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/patients/{patient_id}"
```

### Medication Statements (Mock.Health MedicationStatement)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/medication-statements?patient=Patient/{id}"
```

**Response:**
```json
{
  "resourceType": "Bundle",
  "total": 2,
  "entry": [
    {
      "resource": {
        "id": "med-001",
        "medication": "Ibuprofen 200mg",
        "dosage": "Take 1 tablet twice daily",
        "status": "active"
      }
    }
  ]
}
```

### Allergies

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/allergies?patient=Patient/{id}"
```

### Conditions (Diagnoses)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/conditions?patient=Patient/{id}"
```

### Related Persons (Emergency Contacts)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/related-persons?patient=Patient/{id}"
```

### Emergency Patient Summary (Combined)

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/fhir/patient-summary/{patient_id}"
```

**Response:**
```json
{
  "patient": {...},
  "allergies": [...],
  "medications": [...],
  "conditions": [...],
  "relatedPersons": [...],
  "summary_generated_at": "2026-05-27T10:30:00Z"
}
```

## Direct Client Usage (Python)

Verwende die `MockHealthClient` Klasse für direkte Aufrufe zur Mock.Health API:

### Example 1: Search & Load Medications (wie der User-Snippet)

```python
from backend.app.services.mockhealth_client import MockHealthClient

client = MockHealthClient()

# Search patients
bundle = client.search_patients(given="John", family="Doe")
if bundle.get("entry"):
    patient_id = bundle["entry"][0]["resource"]["id"]
    
    # Get medications for first patient
    meds = client.get_medication_statements(patient_id)
    print(f"Found {meds.get('total', 0)} medications")
```

### Example 2: Get Allergies & Conditions

```python
allergies = client.get_allergies(patient_id)
conditions = client.get_conditions(patient_id)

print(f"Allergies: {allergies.get('total', 0)}")
print(f"Conditions: {conditions.get('total', 0)}")
```

### Example 3: Get Diagnostic Reports (Radiology)

```python
# Get radiology reports (as shown in original code snippet)
reports = client.get_diagnostic_reports(patient_id, category="RAD")
print(f"Found {reports.get('total', 0)} radiology reports")
```

### Example 4: Demo Function

```python
from backend.app.services.mockhealth_client import demo_search_and_load

# Runs the exact flow from user's code snippet
result = demo_search_and_load()
print(f"Patient ID: {result['patient_id']}")
print(f"Radiology Reports: {result['reports'].get('total', 0)}")
```

## Integration Architecture

```
FastAPI Backend (main.py)
    ↓
FHIRService (delegates to Mock.Health)
    ↓
MockHealthService (API header builder)
    ↓
HTTP Client (httpx / requests)
    ↓
Mock.Health FHIR API (https://api.mock.health/fhir)
    ↓
5 FHIR Resources:
  - Patient
  - MedicationStatement
  - AllergyIntolerance
  - Condition
  - RelatedPerson
```

## Caching

Die Standard-TTLs für Cache sind:
- Patient: 1 hour (3600s)
- Medications: 30 minutes (1800s)
- Allergies: 30 minutes (1800s)
- Conditions: 1 hour (3600s)
- Related Persons: 1 hour (3600s)

Überschreibe via Umgebungsvariablen:
```bash
export CACHE_TTL_PATIENT=3600
export CACHE_TTL_MEDICATIONS=1800
export CACHE_TTL_ALLERGIES=1800
export CACHE_TTL_CONDITIONS=3600
export CACHE_TTL_RELATED=3600
```

## Error Handling

Alle Fehler werden geloggt und graceful gehandhabt:

```python
# FHIR server down?
response = client.get_patient("invalid-id")
# Returns: {"error": "..."}

# Invalid parameters?
response = client.search_patients(given="J" * 500)  # Too long
# Returns: {"resourceType": "Bundle", "total": 0, "entry": [], "error": "..."}
```

## Audit Logging

Alle FHIR-Lesevorgänge werden automatisch geloggt (HIPAA-Compliant):

```sql
-- DB audit_logs table gets entries like:
INSERT INTO audit_logs (user_id, action, resource_type, resource_id, reason, timestamp)
VALUES (1, 'FHIR_PATIENT_SEARCH', 'Patient', 'multiple', 'Emergency search', NOW());
```

## Testing

Run tests:
```bash
pytest packages/backend/tests/ -v --cov=packages/backend/app
```

Unit tests for MockHealthClient (mit mocking):
```bash
pytest packages/backend/tests/test_mockhealth_*
```

## Production Deployment

1. Geheime Keys sicher speichern (AWS Secrets Manager, HashiCorp Vault):
   ```bash
   aws secretsmanager create-secret --name aQuickRescue/mockhealth \
     --secret-string '{"api_key":"sk_live..."}'
   ```

2. Environment variables laden (via deployment secrets)

3. In Docker/K8s deployed, z.B.:
   ```dockerfile
   ENV MOCK_HEALTH_API_KEY=${MOCK_HEALTH_API_KEY}
   ENV MOCK_HEALTH_FHIR_URL=https://api.mock.health/fhir
   ```

## Troubleshooting

**Problem:** `Error: MOCK_HEALTH_API_KEY not set`
- **Lösung:** Stelle sicher, dass `env/env.mockhealth` geladen ist oder setze die ENV Variablen manually

**Problem:** `401 Unauthorized`
- **Lösung:** Überprüfe, dass der API Key aktuell ist (token kann ablaufen)

**Problem:** `Connection timeout`
- **Lösung:** Mock.Health kann gelegentlich langsam sein; erhöhe Timeout auf 10s:
  ```python
  with httpx.Client(timeout=10.0) as client:
      response = client.get(url, headers=headers)
  ```

## References

- FHIR Spec: https://www.hl7.org/fhir/
- Mock.Health Docs: https://www.mock.health/
- HAPI FHIR (alternative): https://hapi.fhir.org/baseR4/

