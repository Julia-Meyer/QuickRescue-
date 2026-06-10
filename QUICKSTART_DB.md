# 🎯 Database Setup — Kurzanleitung

## ⚡ Schnellstart (3 Schritte)

### 1️⃣ Datenbank initialisieren

```bash
cd aQuickRescue
python init_db.py --db backend/dev.db --schema backend/database/schema_sqlite.sql --reset
```

Oder mit Bash-Skript:
```bash
./setup_db.sh
```

### 2️⃣ Backend starten

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3️⃣ API-Dokumentation öffnen

Öffne http://localhost:8000/docs im Browser.

---

## 📊 Was wurde erstellt?

### Dateien
- ✅ `backend/database/schema_sqlite.sql` — SQLite3 Schema
- ✅ `init_db.py` — Python Initialisierungs-Skript
- ✅ `setup_db.sh` — Bash Setup-Skript
- ✅ `DATABASE_SETUP.md` — Ausführliche Dokumentation

### Datenbank-Struktur
- 6 Tabellen (users, patient_profiles, emergency_access, audit_logs, access_logs, role_permissions)
- 2 Views (audit_summary, emergency_access_report)
- 20+ Indexes für Performance
- 4 Test-Benutzer pre-loaded
- 12 RBAC-Regeln pre-loaded

### Test-Benutzer (nach init)

```
Username           | Email                 | Role                  
-------------------|----------------------|-----------------------
patient_john       | john@example.com      | PATIENT
responder_alice    | alice@emergency.com   | FIRST_RESPONDER
doctor_bob         | bob@hospital.com      | EMERGENCY_PHYSICIAN
admin_carol        | carol@admin.com       | ADMIN
```

---

## ✨ Verifikation

```bash
# Datenbank inspizieren
sqlite3 backend/dev.db

# SQL-Kommandos im sqlite3-Prompt:
sqlite> SELECT * FROM users;
sqlite> SELECT COUNT(*) FROM role_permissions;
sqlite> .quit
```

---

## 🔗 Nächste Schritte

1. **Backend starten** → API läuft auf http://localhost:8000
2. **Datenbank verwenden** → `DATABASE_URL=sqlite:///./backend/dev.db`
3. **Tests schreiben** → Siehe `packages/backend/tests/`
4. **Migration zu PostgreSQL** → Folge `DATABASE_SETUP.md`

---

Für Details siehe `DATABASE_SETUP.md` im Projekt-Root.

