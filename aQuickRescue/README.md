# aQuickRescue — Kurzbeschreibung

Ein Backend für schnellen, sicheren Zugriff auf lebenswichtige Patientendaten (FHIR).
Ziel: Ersthelfern in Notfällen innerhalb von Sekunden die wichtigsten Informationen (Allergien, aktuelle Medikamente, Notfallkontakte) verfügbar machen — mit vollständigem Audit-Log.

Kurz und knapp:
- Backend: FastAPI (Python)
- Datenquelle: FHIR-Server (Mock.Health / HAPI)
- Auth: OAuth2 / JWT
- Audit: Alle Datenzugriffe werden geloggt

## Schnellstart (lokal)

1. Umgebungsvariablen setzen (oder `env/env.mockhealth` verwenden):

```bash
export MOCK_HEALTH_API_KEY=sk_live_...
export MOCK_HEALTH_FHIR_URL=https://api.mock.health/fhir
export DATABASE_URL=sqlite:///./dev.db
```

2. Abhängigkeiten installieren:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r aQuickRescue/backend/requirements.txt
```

3. Backend starten:

```bash
cd aQuickRescue/backend
uvicorn app.main:app --reload --port 8000
```

4. API-Dokumentation:

Öffne http://localhost:8000/docs

## Wichtige Endpunkte

- `POST /api/v1/auth/login` — Login (returns JWT)
- `GET /api/v1/fhir/patients` — Patientensuche (für berechtigte Rollen)
- `GET /api/v1/fhir/patients/{id}` — Patientendetails
- `GET /api/v1/fhir/medication-statements?patient=Patient/{id}`
- `GET /api/v1/fhir/allergies?patient=Patient/{id}`
- `GET /api/v1/fhir/conditions?patient=Patient/{id}`
- `GET /api/v1/fhir/related-persons?patient=Patient/{id}`
- `GET /api/v1/fhir/patient-summary/{id}` — Kombinierte Notfallübersicht

Alle Endpunkte erfordern Authentifizierung und sind auf Rollen (First Responder / Physician / Admin) beschränkt.

## Entwicklungshinweise

- Cache: In der Entwicklung ein einfacher In-Memory-Cache; Produktion → Redis empfohlen.
- FHIR-Client: In `packages/backend/app/services/mockhealth_client.py` befindet sich ein einfacher Client (Requests).
- Tests: `test_mockhealth.py` ist ein einfacher Smoke-Test für die Mock.Health-Integration.

## Kontakt & Support

- Bugs: GitHub Issues
- Security: security@yourorg.com

---

Kurze README-Version: fokusiert auf Start und wichtigste Endpunkte. Wenn du möchtest, kann ich noch eine schlankere "Developer Quick Reference" oder eine "Ops Checklist" ergänzen.
 
## Schritt-für-Schritt (einfach)

1) Umgebungsvariablen setzen (API‑Key, FHIR‑URL, DB):

```bash
export MOCK_HEALTH_API_KEY=sk_live_...
export MOCK_HEALTH_FHIR_URL=https://api.mock.health/fhir
export DATABASE_URL=sqlite:///./dev.db
```

2) Umgebung & Abhängigkeiten:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r aQuickRescue/backend/requirements.txt
```

3) Backend starten:

```bash
cd aQuickRescue/backend
uvicorn app.main:app --reload --port 8000
```

4) API testen (Beispiel):

```bash
# Patienten suchen (berechtigte Rolle nötig)
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/fhir/patients?family=Smith"

# Notfall‑Zusammenfassung
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/v1/fhir/patient-summary/Patient/123"
```

5) Tests ausführen (lokal):

```bash
python test_mockhealth.py
pytest packages/backend/tests/ -v
```

## Wichtige Funktionen & Dienste (kurz erklärt)

Backend (Hauptfunktionen):
- `POST /api/v1/auth/login` — Authentifiziert einen Benutzer und gibt ein JWT zurück.
- `GET /api/v1/fhir/patients` — Sucht Patienten auf dem FHIR‑Server (given, family, birthdate).
- `GET /api/v1/fhir/patients/{id}` — Holt einen einzelnen Patient (FHIR Resource).
- `GET /api/v1/fhir/medication-statements` — Listet `MedicationStatement` für einen Patienten.
- `GET /api/v1/fhir/allergies` — Listet `AllergyIntolerance` für einen Patienten.
- `GET /api/v1/fhir/conditions` — Listet `Condition` (Diagnosen) für einen Patienten.
- `GET /api/v1/fhir/related-persons` — Listet `RelatedPerson` (Notfallkontakte).
- `GET /api/v1/fhir/patient-summary/{id}` — Kombiniert die obigen Ressourcen zu einer schnellen Notfallübersicht.

Wesentliche Services / Module:
- `app.services.mockhealth_client.MockHealthClient` — Niedrig‑Level HTTP‑Client für Mock.Health (Methoden: `search_patients`, `get_patient`, `get_medication_statements`, `get_allergies`, `get_conditions`, `get_related_persons`, `get_diagnostic_reports`, `demo_search_and_load`).
- `app.services.fhir_service.FHIRService` — Wrapper, der MockHealthClient verwendet, ergänzt um Caching und Logging (Methoden: `search_patient`, `get_patient`, `get_patient_allergies`, `get_patient_medications`, `get_medication_statements`, `get_conditions`, `get_related_persons`).
- `AuditService.log_access(db, user_id, patient_id, action, resource_type, resource_id, reason, ip_address, ...)` — Schreibt Audit‑Einträge in die DB und ins Log.
- Auth‑Utilities: `create_access_token`, `verify_token`, `get_current_user`, `check_role` — JWT‑Erzeugung und Rollenprüfung.

Kurzbeschreibung des Ablaufs einer FHIR‑Abfrage
1. Client (App) ruft einen API‑Endpoint auf (z. B. Patientensuche).
2. FastAPI‑Endpoint prüft Token / Rolle (`get_current_user`).
3. Endpoint ruft `FHIRService` auf, dieser verwendet `MockHealthClient` zum externen FHIR‑Call.
4. Ergebnis wird (optional) gecached, AuditEntry geschrieben und an den Client zurückgegeben.

## Entwicklerhinweise (Tipps)
- Verwende die `MockHealthClient`‑Methoden beim Schreiben von Unit‑Tests (oder mocke HTTPs mit `responses` / `httpx` testing).
- Produktionscache: Redis statt In‑Memory; Konfig über `CACHE_TTL_*` Umgebungsvariablen.
- Für Performance: FHIR‑Aufrufe parallelisieren (bereits im Patienten‑Summary umgesetzt).
