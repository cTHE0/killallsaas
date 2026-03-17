# killallsaas.com

AI-powered open source marketplace. Kill every paid SaaS with a free alternative.

## Stack

- **Backend**: Python / Flask
- **Frontend**: Vanilla JS + CSS (no framework)
- **Storage**: `data.json` (swap with Postgres in production)

## Project structure

```
killallsaas/
├── app.py                     # Flask app + all routes
├── data.json                  # Auto-created on first run (gitignored)
├── .env                       # Secrets — never commit this file
├── .env.example               # Template to share with the team
├── requirements.txt
├── templates/
│   ├── index.html             # Public site
│   ├── admin_login.html       # Admin login
│   ├── admin.html             # Admin dashboard
│   └── admin_tool_form.html   # Add / Edit tool
└── static/
    ├── css/main.css
    └── js/main.js
```

## Local setup

```bash
# 1. Clone
git clone https://github.com/yourname/killallsaas.git
cd killallsaas

# 2. Install
pip install -r requirements.txt

# 3. Configure secrets
cp .env.example .env
# Edit .env with your own values

# 4. Run
python app.py
# → http://localhost:5000
```

## Environment variables

Copy `.env.example` to `.env` and fill in your values. **Never commit `.env`.**

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ADMIN_PASSWORD` | Password for the `/admin` panel |

## Admin panel

→ `https://killallsaas.com/admin`

| Route | Description |
|-------|-------------|
| `GET /admin` | Dashboard — tools + kill requests |
| `GET/POST /admin/tools/add` | Add a new tool |
| `GET/POST /admin/tools/<id>/edit` | Edit a tool |
| `POST /admin/tools/<id>/toggle` | Show / hide a tool |
| `POST /admin/tools/<id>/delete` | Delete a tool |
| `POST /admin/requests/<id>/status` | Mark request done/queued |
| `GET /admin/export` | Download data.json |

## Public API

| Route | Params | Description |
|-------|--------|-------------|
| `GET /api/tools` | `cat`, `sort`, `q`, `tag` | List tools |
| `GET /api/stats` | — | Global stats |
| `POST /api/kill-request` | `saas_name`, `email` | Submit a kill request |
| `GET /api/kill-requests` | — | Kill queue |
| `POST /api/kill-request/<id>/vote` | — | Upvote |

## Deploy on PythonAnywhere

WSGI file:
```python
from app import app as application
```

Set `SECRET_KEY` and `ADMIN_PASSWORD` under **Web > Environment variables**.

## Deploy on Railway / Render / Fly.io

```bash
echo "web: gunicorn app:app" > Procfile
pip install gunicorn
pip freeze > requirements.txt
```

Set env vars in the platform dashboard.
