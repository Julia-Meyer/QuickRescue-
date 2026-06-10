# 🚀 aQuickRescue Frontend - Setup Anleitung

## ⚠️ Problem

Die Frontend-App zeigt im Browser nichts an, weil:
1. **Node.js nicht installiert ist** → npm funktioniert nicht
2. **Dependencies fehlen** → sql.js war nicht in package.json
3. **Dev-Server läuft nicht** → Frontend wird nicht gebaut

---

## ✅ Schritt-für-Schritt Lösung

### **Schritt 1: Node.js installieren**

#### Windows - Automatisch:
```powershell
# Mit winget (falls verfügbar)
winget install OpenJS.NodeJS
```

#### Windows - Manuell:
1. Öffne https://nodejs.org/
2. Lade die **LTS-Version (v20 oder höher)** herunter
3. Starte den Installer
4. ✅ Bestätige alle Standards
5. **PowerShell neu starten**
6. Verifiziere die Installation:
```powershell
node --version    # → sollte v20.x.x zeigen
npm --version     # → sollte 10.x.x zeigen
```

---

### **Schritt 2: Frontend-Dependencies installieren**

```powershell
# In das Frontend-Verzeichnis gehen
cd "C:\Users\Lena\PycharmProjects\QuickRescue-\aQuickRescue\packages\frontend"

# Dependencies installieren
npm install

# Ausgabe sollte zeigen:
# added 100+ packages in 30s
```

---

### **Schritt 3: Dev-Server starten**

```powershell
# Noch im Frontend-Verzeichnis
npm run dev

# Erwartete Ausgabe:
# ➜  Local:   http://localhost:5173/
# ➜  press h + enter to show help
```

---

### **Schritt 4: Im Browser öffnen**

1. Öffne deinen Browser
2. Gehe zu: **http://localhost:5173**
3. Du solltest nun die Anmeldeseite sehen! ✅

---

### **Schritt 5: Mit Demo-Credentials anmelden**

**Verfügbare Accounts:**

| Rolle | Benutzername | Passwort |
|-------|-------------|----------|
| 🚗 Ersthelfer | `responder1` | `password123` |
| 🏥 Patient | `patient1` | `password123` |
| 👨‍⚖️ Admin | `admin1` | `password123` |

---

## 🔧 Häufige Fehler

### ❌ `npm: command not found`
**Lösung:** Node.js ist nicht installiert
```powershell
# Verifiziere Node.js Installation
node --version    # Sollte v20.x.x zeigen
npm --version     # Sollte 10.x.x zeigen
```

### ❌ `ENOENT: no such file or directory, open '...\node_modules'`
**Lösung:** Dependencies fehlen
```powershell
rm -r node_modules package-lock.json
npm install
```

### ❌ Port 5173 bereits in Benutzung
**Lösung:** Anderer Port
```powershell
npm run dev -- --port 5174
```

### ❌ `Cannot find module 'sql.js'`
**Lösung:** sql.js wurde bereits zu package.json hinzugefügt, aber `npm install` neu ausführen
```powershell
npm install
```

---

## 📊 Was wurde repariert

| Problem | Lösung |
|---------|--------|
| ❌ Node.js nicht installiert | ✅ Installation erforderlich |
| ❌ sql.js fehlte | ✅ Zu package.json hinzugefügt |
| ❌ zustand middleware Fehler | ✅ Aus store.js entfernt |
| ❌ Dependencies nicht installiert | ✅ npm install erforderlich |

---

## 🎯 Nach dem Setup

**Frontend lädt zu**:
- `http://localhost:5173` - Entwicklungsserver
- `http://localhost:5173/login` - Anmeldeseite
- `http://localhost:5173/dashboard` - Dashboard (nach Anmeldung)

**Backend muss auch laufen**:
```powershell
cd "C:\Users\Lena\PycharmProjects\QuickRescue-\aQuickRescue\backend"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📞 Support

Falls Probleme auftreten:
1. Prüfe Node.js Version: `node -v`
2. Prüfe npm Version: `npm -v`
3. Lösche node_modules: `rm -r node_modules`
4. Neu installieren: `npm install`
5. Dev-Server neustarten: `npm run dev`

---

**Viel Erfolg! 🚀**

