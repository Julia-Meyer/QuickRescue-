# 🗄️ Database Setup Guide

## Überblick

aQuickRescue nutzt **SQLite3** für die lokale Entwicklung. Für die Produktion wird **PostgreSQL** empfohlen (siehe `backend/database/schema.sql`).

## Schnellstart

### 1. Datenbank initialisieren

```bash
cd aQuickRescue
python init_db.py --db backend/dev.db --schema backend/database/schema_sqlite.sql --reset
```

**Optionen:**
- `--db <path>` — Pfad zur Datenbankdatei (Standard: `dev.db`)
- `--schema <path>` — Pfad zur Schema-Datei (Standard: `schema_sqlite.sql`)
- `--reset` — Datenbank löschen und neu erstellen

### 2. Datenbank überprüfen

```bash
sqlite3 aQuickRescue/backend/dev.db
```

Beispiel-Abfragen im SQLite-Prompt:

```sql
-- Alle Tabellen anzeigen
.tables

-- Anzahl der Benutzer
SELECT COUNT(*) FROM users;

-- Test-Benutzer anzeigen
SELECT username, role FROM users;

-- RBAC-Regeln anzeigen
SELECT role, resource_type, action FROM role_permissions LIMIT 5;

-- Datenbank beenden
.quit
```

## Datenbankstruktur

### Tabellen

| Tabelle | Zweck | Zeilen (initial) |
|---------|-------|------------------|
| `users` | Authentifizierung & Autorisierung | 4 (test users) |
| `patient_profiles` | Patientendaten + FHIR-Referenz | 0 |
| `emergency_access` | Notfallzugriffe auf Patientendaten | 0 |
| `audit_logs` | HIPAA-Audit-Trail (WHO, WHAT, WHEN, WHERE, WHY) | 0 |
| `access_logs` | Misslungene/verdächtige Zugriffe | 0 |
| `role_permissions` | Rollenbasierte Zugriffskontrolle (RBAC) | 12 |

### Views (Berichte)

- **`audit_summary`** — Zusammenfassung der Audit-Logs grouped by date
- **`emergency_access_report`** — Übersicht aller Notfallzugriffe

## Test-Benutzer

Nach der Initialisierung stehen folgende Test-Benutzer zur Verfügung:

| Username | Email | Role | Password Demo |
|----------|-------|------|---------------|
| `patient_john` | john@example.com | PATIENT | `password123` |
| `responder_alice` | alice@emergency.com | FIRST_RESPONDER | `password123` |
| `doctor_bob` | bob@hospital.com | EMERGENCY_PHYSICIAN | `password123` |
| `admin_carol` | carol@admin.com | ADMIN | `password123` |

**Hinweis:** Die Passwörter in der Datenbank sind bcrypt-gehashed. Für Tests muss die Anwendung die Passwörter hashend vergleichen.

## Umgebungsvariablen

```bash
# SQLite (Entwicklung)
DATABASE_URL=sqlite:///./backend/dev.db

# PostgreSQL (Produktion)
DATABASE_URL=postgresql://user:password@localhost:5432/quickrescue
```

## Migration zu PostgreSQL

Für die Produktion folgen Sie diesen Schritten:

1. Installieren Sie PostgreSQL 14+
2. Erstellen Sie eine Datenbank:
   ```sql
   CREATE DATABASE quickrescue;
   ```
3. Führen Sie das Schema aus:
   ```bash
   psql quickrescue < backend/database/schema.sql
   ```
4. Setzen Sie `DATABASE_URL` auf Ihre PostgreSQL-Verbindung

## Häufige Aufgaben

### Datenbank zurücksetzen

```bash
python init_db.py --db backend/dev.db --schema backend/database/schema_sqlite.sql --reset
```

### Datenbank in der Anwendung verwenden

```python
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./backend/dev.db")
```

### Audit-Logs anzeigen

```bash
sqlite3 backend/dev.db "SELECT timestamp, username, action, status FROM audit_logs ORDER BY timestamp DESC LIMIT 10;"
```

### Notfallzugriffe auditieren

```bash
sqlite3 backend/dev.db "
  SELECT 
    ea.accessed_at,
    u.username,
    pp.first_name || ' ' || pp.last_name as patient,
    ea.reason,
    ea.status
  FROM emergency_access ea
  JOIN users u ON ea.responder_id = u.id
  JOIN patient_profiles pp ON ea.patient_id = pp.id
  ORDER BY ea.accessed_at DESC;
"
```

## Sicherheitshinweise

- ✅ Alle Passwörter sind bcrypt-gehashed
- ✅ Audit-Logs sind unveränderbar (nur INSERT/SELECT)
- ✅ Rollenbasierte Zugriffskontrolle (RBAC)
- ✅ Constraints auf HIPAA-Audit-Trail
- ⚠️ SQLite ist nicht für Produktion gedacht — PostgreSQL verwenden

## Datenbankdateien

| Datei | Zweck |
|-------|-------|
| `backend/database/schema.sql` | PostgreSQL Schema (Produktion) |
| `backend/database/schema_sqlite.sql` | SQLite3 Schema (Entwicklung) |
| `init_db.py` | Datenbank-Initialisierungs-Skript |
| `backend/dev.db` | Lokale Entwicklung DB (nach init) |

---

**Weitere Hilfe:** Siehe `README.md` im Projekt-Root.

