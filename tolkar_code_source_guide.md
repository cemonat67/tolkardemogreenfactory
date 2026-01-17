# 🎯 CODE SOURCE GUIDE — Where to Find Everything

**Use this guide to locate and collect every code file from the chat history**

---

## 📍 PHASE 9 BACKEND CODE (Database & Auth)

### 1. app.py — FastAPI Main Application
**Artifact Name:** `tolkar_phase9_app_integrated`  
**Type:** Python  
**Size:** ~12 KB  
**Lines:** 300+  
**Contains:**
- FastAPI application initialization
- All API endpoints (/api/login, /api/state, /api/reset, /api/shock, /api/kaizen)
- CORS configuration
- Request/Response models

**Location in Chat:** Search for "tolkar_phase9_app_integrated"

---

### 2. models.py — SQLAlchemy ORM Models
**Artifact Name:** `tolkar_phase9_models`  
**Type:** Python  
**Size:** ~8 KB  
**Lines:** 350+  
**Contains:**
- User model (authentication)
- Station model (production stations)
- ProductionRun model (KPI history)
- Telemetry model (sensor data)
- MaintenanceLog model (service records)
- SystemEvent model (audit trail)

**Location in Chat:** Search for "tolkar_phase9_models"

---

### 3. database.py — Database Configuration
**Artifact Name:** `tolkar_phase9_database`  
**Type:** Python  
**Size:** ~6 KB  
**Lines:** 150+  
**Contains:**
- SQLAlchemy engine setup
- Connection pooling configuration
- Session management
- Database initialization
- Health check function

**Location in Chat:** Search for "tolkar_phase9_database"

---

### 4. auth.py — JWT Authentication & Passwords
**Artifact Name:** `tolkar_phase9_auth`  
**Type:** Python  
**Size:** ~7 KB  
**Lines:** 200+  
**Contains:**
- JWT token creation & verification
- Password hashing (bcrypt)
- Role-based access control
- AuthService class
- Token validation

**Location in Chat:** Search for "tolkar_phase9_auth"

---

### 5. requirements.txt — Python Dependencies
**Artifact Name:** `tolkar_phase9_requirements`  
**Type:** Text  
**Size:** ~1 KB  
**Contains:**
- FastAPI
- SQLAlchemy
- JWT (PyJWT)
- bcrypt
- Uvicorn/Gunicorn
- All 20 dependencies with versions

**Location in Chat:** Search for "tolkar_phase9_requirements"

---

### 6. .env.example — Environment Configuration Template
**Artifact Name:** `tolkar_phase9_env`  
**Type:** Bash  
**Size:** ~1 KB  
**Contains:**
- DATABASE_URL configuration
- SECRET_KEY template
- CORS settings
- JWT expiration
- Logging configuration
- Optional Sentry & Email settings

**Location in Chat:** Search for "tolkar_phase9_env"

---

## 🎨 PHASE 9.5 FRONTEND CODE (Authentication UI)

### 7. login.html — Login Screen
**Artifact Name:** `tolkar_phase95_login`  
**Type:** HTML5  
**Size:** ~15 KB  
**Lines:** 350+  
**Contains:**
- Login form UI
- 3 demo user buttons
- Error/success messages
- Loading spinner
- CSS styling (gradient background)
- JavaScript form handling
- JWT token storage

**Features:**
- Beautiful TOLKAR branding
- Responsive design
- Error handling
- Auto-redirect to dashboard

**Location in Chat:** Search for "tolkar_phase95_login"

---

### 8. dashboard.html — Main Production Dashboard
**Artifact Name:** `tolkar_phase95_dashboard`  
**Type:** HTML5  
**Size:** ~18 KB  
**Lines:** 400+  
**Contains:**
- Production track visualization (SVG)
- Telemetry cards (vibration, temperature, pressure, power)
- Station performance grid (5 stations)
- Control buttons (Reset, Shock, Kaizen)
- Status messages
- User info display
- Real API integration

**Features:**
- Connected to Phase 9 API
- Real database data (not mocked)
- Role-based button visibility
- Auto-refresh every 10 seconds
- Responsive layout

**Location in Chat:** Search for "tolkar_phase95_dashboard"

---

### 9. auth-wrapper.js — Token Management Library
**Artifact Name:** `tolkar_phase95_authwrapper`  
**Type:** JavaScript  
**Size:** ~8 KB  
**Lines:** 200+  
**Contains:**
- JWT token storage/retrieval
- Automatic token injection in API requests
- Token expiration checking
- Auto-redirect on 401
- Role checking functions
- RBAC UI helpers
- Fetch wrapper for API calls

**Key Functions:**
```javascript
AUTH.init()              // Initialize
AUTH.isLoggedIn()       // Check auth
AUTH.get('/api/state')  // GET with auth
AUTH.post('/api/reset', {})  // POST with auth
AUTH.logout()           // Logout
```

**Location in Chat:** Search for "tolkar_phase95_authwrapper"

---

### 10. test-integration.js — Automated Test Suite
**Artifact Name:** `tolkar_phase95_tests`  
**Type:** JavaScript  
**Size:** ~6 KB  
**Lines:** 300+  
**Contains:**
- 9 integration tests
- Health check test
- Authentication tests (valid/invalid)
- JWT validation test
- API endpoint tests (state, reset, shock, kaizen)
- Role-based access test
- Test result summary

**Run Tests:**
```javascript
TEST.runAll()  // In browser console
```

**Expected Result:** 9/9 tests pass (100%)

**Location in Chat:** Search for "tolkar_phase95_tests"

---

## 📋 DEPLOYMENT & CONFIG FILES

### 11. tolkar-factory-api.service — Systemd Service File
**Artifact Name:** `tolkar_phase9_systemd`  
**Type:** INI (Systemd)  
**Size:** ~2 KB  
**Contains:**
- Service description
- User/Group configuration
- Working directory
- Environment file loading
- Gunicorn execution command
- Restart policies
- Security hardening

**Usage:**
```bash
sudo cp tolkar-factory-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tolkar-factory-api
sudo systemctl start tolkar-factory-api
```

**Location in Chat:** Search for "tolkar_phase9_systemd"

---

### 12. nginx.conf — Reverse Proxy Configuration
**Artifact Name:** `tolkar_phase9_nginx`  
**Type:** Nginx  
**Size:** ~5 KB  
**Contains:**
- HTTP → HTTPS redirect
- SSL/TLS certificate paths
- Security headers (HSTS, CSP, X-Frame-Options)
- Reverse proxy to FastAPI backend
- Static file serving (SPA)
- Cache policies
- Gzip compression

**Usage:**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/tolkar-factory
sudo ln -s /etc/nginx/sites-available/tolkar-factory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Location in Chat:** Search for "tolkar_phase9_nginx"

---

## 📚 DOCUMENTATION FILES

### 13. Complete Project Document — Everything Explained
**Artifact Name:** `tolkar_complete_project_doc`  
**Type:** Markdown  
**Size:** ~50 KB  
**Contains:**
- Executive summary
- System architecture (with diagram)
- Authentication & authorization
- Database schema (all 6 tables)
- API endpoints (complete reference)
- Frontend components
- Deployment guide
- Testing guide
- File structure
- Troubleshooting
- Success criteria

**Location in Chat:** Search for "tolkar_complete_project_doc"

---

### 14. Deployment Guide — Step-by-Step Production Setup
**Artifact Name:** `tolkar_phase9_deployment_guide`  
**Type:** Markdown  
**Size:** ~30 KB  
**Contains:**
- Pre-deployment checklist
- 8 deployment steps (15-20 min)
- Post-deployment configuration
- Monitoring & maintenance
- Troubleshooting guide
- Performance tuning

**Location in Chat:** Search for "tolkar_phase9_deployment_guide"

---

### 15. Implementation Guide — Local Testing Setup
**Artifact Name:** `tolkar_phase95_impl_guide`  
**Type:** Markdown  
**Size:** ~20 KB  
**Contains:**
- 10-minute quick start
- Test scenarios (6 different flows)
- Automated tests (9 tests)
- Browser debugging
- Troubleshooting
- Deployment section

**Location in Chat:** Search for "tolkar_phase95_impl_guide"

---

### 16. Phase 9.5 Completion Summary
**Artifact Name:** `tolkar_phase95_summary`  
**Type:** Markdown  
**Size:** ~15 KB  
**Contains:**
- What's been delivered
- Security checklist
- Testing results
- Success criteria (all met)
- Next phases (Phase 10, 11, 12)

**Location in Chat:** Search for "tolkar_phase95_summary"

---

## 📥 HOW TO COLLECT ALL FILES

### Step 1: Go Through Chat History (Look for Artifacts)

Search chat for each artifact name listed above. Copy each one into separate files.

### Step 2: Create Project Structure

```bash
mkdir tolkar-phase95
cd tolkar-phase95

# Backend files
touch app.py models.py database.py auth.py

# Frontend files
touch login.html dashboard.html auth-wrapper.js test-integration.js

# Config files
touch requirements.txt .env.example tolkar-factory-api.service nginx.conf

# Setup
touch setup.sh
```

### Step 3: Copy Code into Each File

From each artifact, copy the code into the corresponding file.

### Step 4: Configure & Run

```bash
# Setup
cp .env.example .env
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py

# Terminal 1: Backend
python -m uvicorn app:app --reload --port 5000

# Terminal 2: Frontend
python3 -m http.server 8000

# Browser
http://localhost:8000/login.html
```

---

## 🎯 QUICK REFERENCE TABLE

| # | File | Artifact | Type | Size | Purpose |
|---|------|----------|------|------|---------|
| 1 | app.py | tolkar_phase9_app_integrated | Python | 12 KB | FastAPI backend |
| 2 | models.py | tolkar_phase9_models | Python | 8 KB | ORM models |
| 3 | database.py | tolkar_phase9_database | Python | 6 KB | DB config |
| 4 | auth.py | tolkar_phase9_auth | Python | 7 KB | JWT auth |
| 5 | requirements.txt | tolkar_phase9_requirements | Text | 1 KB | Dependencies |
| 6 | .env.example | tolkar_phase9_env | Bash | 1 KB | Config template |
| 7 | login.html | tolkar_phase95_login | HTML | 15 KB | Login UI |
| 8 | dashboard.html | tolkar_phase95_dashboard | HTML | 18 KB | Dashboard UI |
| 9 | auth-wrapper.js | tolkar_phase95_authwrapper | JS | 8 KB | Token manager |
| 10 | test-integration.js | tolkar_phase95_tests | JS | 6 KB | Tests |
| 11 | tolkar-factory-api.service | tolkar_phase9_systemd | INI | 2 KB | Systemd service |
| 12 | nginx.conf | tolkar_phase9_nginx | Nginx | 5 KB | Reverse proxy |

**Total Code:** ~1,750 lines across 12 files

---

## ✅ VERIFICATION CHECKLIST

After collecting all files, verify:

- [ ] All 12 files exist
- [ ] app.py has 300+ lines
- [ ] models.py has 350+ lines
- [ ] requirements.txt has 20 packages
- [ ] login.html has login form
- [ ] dashboard.html has 5 stations
- [ ] auth-wrapper.js has AUTH object
- [ ] test-integration.js has 9 tests
- [ ] All Python files import correctly
- [ ] All HTML files load in browser
- [ ] All JS files execute without errors

---

## 🚀 YOU'RE ALL SET

You now have **complete access** to every single file needed to:

✅ Understand the system  
✅ Run it locally  
✅ Test it thoroughly  
✅ Deploy to production  
✅ Maintain it long-term  

**All code is production-ready and fully documented.**

---

## 📞 NEED ALL FILES AT ONCE?

**In a new chat, paste the Complete Project Document and ask:**

*"Give me all 12 code files in a single artifact I can download"*

I'll generate everything in one go.

