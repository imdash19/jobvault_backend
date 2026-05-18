# JobVault — Job Application Tracker API

A production-ready **Django REST Framework** backend for tracking job applications with JWT authentication, filtering, file uploads, and dashboard analytics.

---

## Tech Stack

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.17-red?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-SimpleJWT-000000?style=flat&logo=jsonwebtokens&logoColor=white)

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Framework | Django 5.2 |
| API | Django REST Framework 3.17 |
| Authentication | SimpleJWT (JWT Bearer Tokens) |
| Database | PostgreSQL |
| Filtering | django-filter |
| CORS | django-cors-headers |
| Config | python-decouple (.env) |
| File Handling | Pillow |

---

## Features

- **JWT Authentication** — Register, Login, Logout (token blacklist), Token Refresh
- **Job Application CRUD** — Create, Read, Update, Delete with ownership enforcement
- **Filtering & Search** — Filter by status, platform, date range; search by company/role
- **Ordering & Pagination** — Sort by any field, 20 results per page
- **Resume Upload** — PDF/DOC/DOCX, max 5 MB, stored in `media/resumes/`
- **Dashboard Analytics** — Overall stats, monthly trends, platform & status breakdown
- **User Isolation** — Users can only access their own applications
- **CORS Ready** — Configured for React frontend integration
- **Admin Panel** — Full Django admin with filters and search

---

## Project Structure

```
jobvault_backend/
│
├── manage.py
├── requirements.txt
├── .env                        ← your secrets (never commit)
├── .env.example                ← template
│
├── jobvault_backend/           ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                   ← Authentication app
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── applications/               ← Job Applications app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   ├── filters.py
│   ├── admin.py
│   └── urls.py
│
└── media/                      ← Resume uploads (auto-created)
    └── resumes/
```

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/jobvault_backend.git
cd jobvault_backend
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL

```sql
CREATE DATABASE jobvault_db;
-- Or with a dedicated user:
CREATE USER jobvault_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE jobvault_db TO jobvault_user;
```

### 5. Configure Environment Variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-very-secret-django-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=jobvault_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ACCESS_TOKEN_LIFETIME_MINUTES=60
REFRESH_TOKEN_LIFETIME_DAYS=7
```

> Generate a secret key:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional — for admin panel
```

### 7. Start the Server

```bash
python manage.py runserver
```

API is live at: `http://127.0.0.1:8000`  
Admin panel: `http://127.0.0.1:8000/admin/`

---

## API Endpoints

> **Base URL (local):** `http://127.0.0.1:8000`  
> **Base URL (production):** `https://imdash19.pythonanywhere.com`  
> All protected endpoints require: `Authorization: Bearer <access_token>`

---

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register/` | ❌ | Create new account |
| `POST` | `/api/auth/login/` | ❌ | Get access + refresh tokens |
| `POST` | `/api/auth/logout/` | ✅ | Blacklist refresh token |
| `POST` | `/api/auth/token/refresh/` | ❌ | Refresh access token |
| `GET` | `/api/auth/profile/` | ✅ | Get current user profile |
| `PATCH` | `/api/auth/profile/` | ✅ | Update profile |
| `POST` | `/api/auth/change-password/` | ✅ | Change password |

#### Register — `POST /api/auth/register/`
```json
// Request
{
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "StrongPass@123",
  "confirm_password": "StrongPass@123"
}

// Response 201
{
  "message": "Account created successfully.",
  "user": { "id": 1, "username": "johndoe", "email": "john@example.com" },
  "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
}
```

#### Login — `POST /api/auth/login/`
```json
// Request
{ "username": "johndoe", "password": "StrongPass@123" }

// Response 200
{ "access": "eyJ...", "refresh": "eyJ..." }
```

---

### Job Applications

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/applications/` | List all (paginated) |
| `POST` | `/api/applications/` | Create new |
| `GET` | `/api/applications/{id}/` | Get single |
| `PATCH` | `/api/applications/{id}/` | Partial update |
| `PUT` | `/api/applications/{id}/` | Full update |
| `DELETE` | `/api/applications/{id}/` | Delete |

#### Create Application — `POST /api/applications/`
```json
// Request (application/json)
{
  "company_name": "Google",
  "job_role": "Backend Engineer",
  "job_description": "Build scalable APIs",
  "applied_platform": "LinkedIn",
  "job_url": "https://careers.google.com/job/123",
  "status": "Applied",
  "notes": "Referred by Jane"
}
// applied_date is optional — defaults to today
```

#### Query Parameters (for GET list)

| Parameter | Example | Description |
|---|---|---|
| `search` | `?search=Google` | Search company name or job role |
| `status` | `?status=Applied` | Filter by status |
| `applied_platform` | `?applied_platform=LinkedIn` | Filter by platform |
| `applied_date` | `?applied_date=2024-06-01` | Exact date filter |
| `applied_date_from` | `?applied_date_from=2024-01-01` | Date range start |
| `applied_date_to` | `?applied_date_to=2024-06-30` | Date range end |
| `ordering` | `?ordering=-applied_date` | Sort (prefix `-` = descending) |
| `page` | `?page=2` | Pagination |

---

### Dashboard

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/stats/` | Total, rejected, interview, offer counts |
| `GET` | `/api/dashboard/monthly/` | Monthly trend (last 12 months) |
| `GET` | `/api/dashboard/platform/` | Count by platform |
| `GET` | `/api/dashboard/status/` | Count by status |

#### Stats Response
```json
{
  "total": 42, "applied": 15, "assessments": 5,
  "interviews": 8, "hr_round": 3, "rejected": 10,
  "offers": 3, "joined": 1
}
```

---

## Valid Choice Values

### Application Status
`Applied` · `Assessment` · `Interview Scheduled` · `HR Round` · `Rejected` · `Offer Received` · `Joined`

### Applied Platform
`LinkedIn` · `Naukri` · `Indeed` · `Wellfound` · `Internshala` · `Foundit` · `Company Website` · `Referral` · `Other`

---

## Resume Upload

Send as `multipart/form-data` with field name `resume`.

- **Allowed formats:** `.pdf`, `.doc`, `.docx`
- **Max file size:** 5 MB

```bash
# Example with curl
curl -X PATCH https://imdash19.pythonanywhere.com/api/applications/1/ \
  -H "Authorization: Bearer <token>" \
  -F "resume=@/path/to/resume.pdf" \
  -F "status=Interview Scheduled"
```

---

## Security

| Rule | Detail |
|---|---|
| Protected endpoints | Require valid JWT Bearer token |
| Ownership enforcement | Users only access their own applications |
| Token expiry | Access: 60 min · Refresh: 7 days |
| Logout | Blacklists refresh token permanently |
| Passwords | PBKDF2 + SHA256 hashing |
| Future dates | Rejected at validation level |
| File uploads | Extension + size validated server-side |

---

## Deployment (PythonAnywhere)

### 1. Upload Code
```bash
# In PythonAnywhere Bash console
git clone https://github.com/yourusername/jobvault_backend.git
```

### 2. Create Virtualenv & Install
```bash
cd ~/jobvault_backend
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `.env`
```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=imdash19.pythonanywhere.com
DB_NAME=imdash19$jobvault_db
DB_USER=imdash19
DB_PASSWORD=your_db_password
DB_HOST=imdash19.mysql.pythonanywhere-services.com
DB_PORT=3306
CORS_ALLOWED_ORIGINS=https://yourfrontend.com
```

### 4. Migrate & Collect Static
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

### 5. WSGI File

Replace the contents of your PythonAnywhere WSGI file with:

```python
import os, sys
path = '/home/imdash19/jobvault_backend'
if path not in sys.path:
    sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'jobvault_backend.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 6. Static Files Mapping (Web Tab)

| URL | Directory |
|---|---|
| `/static/` | `/home/imdash19/jobvault_backend/staticfiles` |
| `/media/` | `/home/imdash19/jobvault_backend/media` |

### 7. Reload the web app ✅

---

## Frontend Integration (React + Axios)

```js
// src/api/axios.js
import axios from 'axios';

const API = axios.create({
  baseURL: 'https://imdash19.pythonanywhere.com',
});

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default API;
```

```js
// Login and save tokens
const res = await API.post('/api/auth/login/', { username, password });
localStorage.setItem('access_token', res.data.access);
localStorage.setItem('refresh_token', res.data.refresh);

// Fetch applications with filters
const res = await API.get('/api/applications/', {
  params: { status: 'Applied', ordering: '-applied_date' }
});

// Get dashboard stats
const res = await API.get('/api/dashboard/stats/');
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | ✅ | — | Django secret key |
| `DEBUG` | ✅ | `False` | Debug mode |
| `ALLOWED_HOSTS` | ✅ | — | Comma-separated hosts |
| `DB_NAME` | ✅ | `jobvault_db` | Database name |
| `DB_USER` | ✅ | `postgres` | Database user |
| `DB_PASSWORD` | ✅ | — | Database password |
| `DB_HOST` | ✅ | `localhost` | Database host |
| `DB_PORT` | ✅ | `5432` | Database port |
| `CORS_ALLOWED_ORIGINS` | ✅ | — | Frontend origins |
| `ACCESS_TOKEN_LIFETIME_MINUTES` | ❌ | `60` | JWT access token life |
| `REFRESH_TOKEN_LIFETIME_DAYS` | ❌ | `7` | JWT refresh token life |

---

## License

MIT License — free to use for personal and commercial projects.

---

*Built with ❤️ using Django REST Framework*
