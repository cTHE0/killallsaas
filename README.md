# killallsaas.com

AI-powered open source marketplace. Kill every paid SaaS with a free alternative.

## Stack
- **Backend**: Python / Flask
- **Frontend**: Vanilla JS + CSS (no framework)
- **Fonts**: Bebas Neue + DM Mono + DM Sans

## Project structure

```
killallsaas/
├── app.py                  # Flask app + all API routes
├── requirements.txt
├── templates/
│   └── index.html          # Main page (Jinja2 template)
└── static/
    ├── css/
    │   └── main.css        # All styles
    └── js/
        └── main.js         # Frontend logic (fetches from API)
```

## API routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Main page |
| GET | `/api/tools` | List tools (filter: `cat`, `sort`, `q`, `tag`) |
| GET | `/api/tools/<id>` | Single tool detail |
| GET | `/api/stats` | Global stats |
| POST | `/api/kill-request` | Submit a SaaS to kill |
| GET | `/api/kill-requests` | Kill queue |
| POST | `/api/kill-request/<id>/vote` | Upvote a kill request |

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run
python app.py

# 3. Open
open http://localhost:5000
```

## Production (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Deploy to Railway / Render / Fly.io

```bash
# Add Procfile
echo "web: gunicorn app:app" > Procfile

# Push to GitHub and connect to Railway
# Set PORT env var if needed
```

## Next steps

- [ ] Connect to Postgres/Supabase (replace in-memory TOOLS list)
- [ ] Add AI generation pipeline (Claude API → generate tool on demand)
- [ ] Add X bot (post tweet on every new kill)
- [ ] Add user accounts + GitHub OAuth
- [ ] Add tool rating / review system
