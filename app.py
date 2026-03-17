import json, os, uuid
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, jsonify, request, abort, redirect, url_for, session

# Load .env file if present (local dev). On PythonAnywhere / Railway, set env vars in the dashboard.
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

_load_dotenv()

app = Flask(__name__)

# SECRET_KEY must be set in .env or environment — no fallback in production
app.secret_key = os.environ.get("SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("SECRET_KEY environment variable is not set. Copy .env.example to .env and fill in your values.")

# ─── CONFIG ──────────────────────────────────────────────────
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
    raise RuntimeError("ADMIN_PASSWORD environment variable is not set. Copy .env.example to .env and fill in your values.")
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

# ─── PERSISTENCE ─────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"tools": DEFAULT_TOOLS[:], "kill_requests": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ─── DEFAULT TOOLS ───────────────────────────────────────────
DEFAULT_TOOLS = [
    {"id":"pixelforge","name":"PixelForge","icon":"🎨","cat":"design","kills":"Adobe Photoshop","saving":"$55/mo","saving_yearly":660,"desc":"Full browser-based image editor. Layers, masks, filters, RAW support. Works like Photoshop — no install, no subscription.","features":["Layers & blend modes","Non-destructive filters","RAW support","Brush & selection tools","Color grading","Export PNG/JPG/WebP","Masks & clipping","Plugin support"],"tags":["online","design"],"users":"14.2k","stars":"9.1k","gen_time":"54s","deploy":"# Open right now\nhttps://photopea.com\n\n# Self-host\ndocker run -p 3000:3000 nicedoc/photopea","online_url":"https://photopea.com","github_url":"https://github.com/nicktindall/cyclon.p2p","is_new":False,"kills_count":1247,"created_at":"2024-01-15","active":True},
    {"id":"designforge","name":"DesignForge","icon":"✏️","cat":"design","kills":"Figma","saving":"$45/editor/mo","saving_yearly":540,"desc":"Collaborative vector design tool. Real-time multiplayer, components, auto-layout, prototyping — all in the browser.","features":["Real-time collaboration","Vector editing","Components & variants","Auto-layout","Prototyping & flows","Asset export","Dark mode","REST API"],"tags":["online","selfhost"],"users":"19.8k","stars":"15.3k","gen_time":"63s","deploy":"# Launch online\nhttps://penpot.app\n\n# Self-host\ndocker run -p 3449:3449 penpotapp/frontend","online_url":"https://penpot.app","github_url":"https://github.com/penpot/penpot","is_new":True,"kills_count":2891,"created_at":"2024-03-01","active":True},
    {"id":"drawpad","name":"DrawPad","icon":"🖊️","cat":"design","kills":"Miro / FigJam","saving":"$16/mo","saving_yearly":192,"desc":"Infinite collaborative whiteboard. Sticky notes, shapes, diagrams, real-time cursors.","features":["Infinite canvas","Real-time cursors","Sticky notes","Diagrams & shapes","Image embed","Export SVG/PNG","Guest access","Keyboard shortcuts"],"tags":["online","selfhost"],"users":"11.4k","stars":"8.7k","gen_time":"38s","deploy":"# Online now\nhttps://excalidraw.com\n\n# Self-host\ndocker run -p 80:80 excalidraw/excalidraw","online_url":"https://excalidraw.com","github_url":"https://github.com/excalidraw/excalidraw","is_new":False,"kills_count":743,"created_at":"2024-01-20","active":True},
    {"id":"opennote","name":"OpenNote","icon":"📝","cat":"productivity","kills":"Notion","saving":"$16/user/mo","saving_yearly":192,"desc":"All-in-one workspace. Notes, databases, kanban, wikis, docs. Full Notion replacement.","features":["Rich text editor","Databases & views","Kanban boards","Team wiki","Page sharing","Import from Notion","Mobile apps","API access"],"tags":["online","selfhost"],"users":"34.6k","stars":"24.2k","gen_time":"48s","deploy":"# Hosted free\nhttps://appflowy.io\n\n# Self-host\ndocker run -p 8080:8080 appflowyinc/appflowy-cloud","online_url":"https://appflowy.io","github_url":"https://github.com/AppFlowy-IO/AppFlowy","is_new":False,"kills_count":4821,"created_at":"2024-01-01","active":True},
    {"id":"gridbase","name":"GridBase","icon":"🗂️","cat":"productivity","kills":"Airtable","saving":"$24/mo","saving_yearly":288,"desc":"Spreadsheet meets database. Grid, kanban, gallery, calendar views. Automations, forms, API.","features":["Grid / Kanban / Gallery","Automations","Forms & surveys","Field relationships","API & webhooks","Import CSV/Excel","Formulas","Permissions"],"tags":["online","selfhost"],"users":"16.2k","stars":"12.8k","gen_time":"52s","deploy":"# Online\nhttps://nocodb.com\n\n# Self-host\ndocker run -p 8080:8080 nocodb/nocodb","online_url":"https://nocodb.com","github_url":"https://github.com/nocodb/nocodb","is_new":False,"kills_count":2341,"created_at":"2024-01-10","active":True},
    {"id":"taskflow","name":"TaskFlow","icon":"✅","cat":"productivity","kills":"Asana / Monday","saving":"$30/mo","saving_yearly":360,"desc":"Project management with kanban, Gantt timeline, and list views. Subtasks, dependencies, time tracking.","features":["Kanban & list","Gantt timeline","Subtasks","Dependencies","Time tracking","Reports","Guest access","Mobile app"],"tags":["online","selfhost"],"users":"24.1k","stars":"19.6k","gen_time":"39s","deploy":"# Hosted free\nhttps://plane.so\n\n# Self-host\ndocker-compose up -d","online_url":"https://plane.so","github_url":"https://github.com/makeplane/plane","is_new":True,"kills_count":1987,"created_at":"2024-02-20","active":True},
    {"id":"bookitfree","name":"BookItFree","icon":"📅","cat":"productivity","kills":"Calendly","saving":"$12/mo","saving_yearly":144,"desc":"Share your calendar link, let anyone book. Integrates with Google Calendar, Outlook.","features":["Availability rules","Booking page","Calendar sync","Email reminders","Round-robin","Group events","Payment collection","Embed widget"],"tags":["online","selfhost"],"users":"9.4k","stars":"7.2k","gen_time":"31s","deploy":"# Hosted free\nhttps://cal.com\n\n# Self-host\ndocker run -p 3000:3000 calcom/cal.com","online_url":"https://cal.com","github_url":"https://github.com/calcom/cal.com","is_new":False,"kills_count":891,"created_at":"2024-01-25","active":True},
    {"id":"opencrm","name":"OpenCRM","icon":"🤝","cat":"crm","kills":"HubSpot","saving":"$800/mo","saving_yearly":9600,"desc":"Full CRM — pipeline management, contact enrichment, email sequences, analytics.","features":["Contact management","Deal pipelines","Email sequences","Call tracking","Reports & analytics","Lead scoring","Web forms","REST API"],"tags":["online","selfhost"],"users":"9.8k","stars":"7.8k","gen_time":"91s","deploy":"# Hosted free\nhttps://twenty.com\n\n# Self-host\ndocker-compose up","online_url":"https://twenty.com","github_url":"https://github.com/twentyhq/twenty","is_new":True,"kills_count":634,"created_at":"2024-03-05","active":True},
    {"id":"mailfree","name":"MailFree","icon":"📧","cat":"crm","kills":"Mailchimp","saving":"$35/mo","saving_yearly":420,"desc":"Email marketing platform. Drag-and-drop builder, automations, segmentation, A/B testing.","features":["Drag & drop builder","Automations","Segmentation","A/B testing","Analytics","Templates","Landing pages","SMTP delivery"],"tags":["online","selfhost"],"users":"18.1k","stars":"13.4k","gen_time":"46s","deploy":"# Self-host\ndocker run -d -p 9000:9000 listmonk/listmonk:latest","online_url":"https://listmonk.app","github_url":"https://github.com/knadh/listmonk","is_new":False,"kills_count":1543,"created_at":"2024-01-18","active":True},
    {"id":"freechat","name":"FreeChat","icon":"💬","cat":"communication","kills":"Slack","saving":"$8/user/mo","saving_yearly":96,"desc":"Team messaging with channels, threads, video calls, screen sharing, and full-text search.","features":["Channels & threads","Video calls","Screen sharing","File sharing","Full-text search","Bots & apps","Mobile apps","E2E encryption"],"tags":["online","selfhost"],"users":"44.8k","stars":"36.2k","gen_time":"44s","deploy":"# Docker\ndocker run -e ROOT_URL=http://localhost -p 3000:3000 rocket.chat","online_url":"https://rocket.chat","github_url":"https://github.com/RocketChat/Rocket.Chat","is_new":False,"kills_count":5214,"created_at":"2024-01-01","active":True},
    {"id":"meetfree","name":"MeetFree","icon":"📹","cat":"communication","kills":"Zoom","saving":"$15/mo","saving_yearly":180,"desc":"Video conferencing for up to 100 people. Recording, waiting room, breakout rooms. No app needed.","features":["HD video & audio","Screen sharing","Recording","Waiting room","Breakout rooms","Polls","Whiteboard","No app needed"],"tags":["online"],"users":"21.6k","stars":"16.8k","gen_time":"58s","deploy":"# No account needed\nhttps://meet.jit.si\n\n# Self-host\ndocker-compose up","online_url":"https://meet.jit.si","github_url":"https://github.com/jitsi/jitsi-meet","is_new":False,"kills_count":2876,"created_at":"2024-01-12","active":True},
    {"id":"autoflow","name":"AutoFlow","icon":"⚡","cat":"automation","kills":"Zapier","saving":"$49/mo","saving_yearly":588,"desc":"Visual workflow automation with 400+ integrations. Build complex multi-step workflows without code.","features":["400+ integrations","Visual builder","Branches & conditions","Error handling","Webhooks","Cron jobs","Data transform","Self-hosted"],"tags":["online","selfhost"],"users":"26.4k","stars":"21.7k","gen_time":"57s","deploy":"# Free tier\nhttps://n8n.io\n\n# Self-host\ndocker run -p 5678:5678 n8nio/n8n","online_url":"https://n8n.io","github_url":"https://github.com/n8n-io/n8n","is_new":False,"kills_count":3421,"created_at":"2024-01-08","active":True},
    {"id":"statsopen","name":"StatsOpen","icon":"📊","cat":"analytics","kills":"Google Analytics","saving":"privacy","saving_yearly":0,"desc":"Privacy-first web analytics. No cookies, GDPR compliant, real-time dashboard.","features":["No cookies","GDPR / CCPA","Real-time","Custom events","Funnels","UTM tracking","Goals","Public dashboards"],"tags":["online","selfhost"],"users":"41.3k","stars":"31.8k","gen_time":"29s","deploy":"# Free (10k pv)\nhttps://plausible.io\n\n# Self-host\ndocker run -p 8000:8000 plausible/analytics","online_url":"https://plausible.io","github_url":"https://github.com/plausible/analytics","is_new":False,"kills_count":6234,"created_at":"2024-01-01","active":True},
    {"id":"heatmapper","name":"HeatMapper","icon":"🔥","cat":"analytics","kills":"Hotjar","saving":"$99/mo","saving_yearly":1188,"desc":"Session recording, heatmaps, click maps, funnel analysis. GDPR safe.","features":["Session recording","Heatmaps","Click maps","Funnels","Rage click detection","Surveys","A/B testing","GDPR safe"],"tags":["online","selfhost"],"users":"8.1k","stars":"6.4k","gen_time":"67s","deploy":"# Self-host\ndocker-compose up -d","online_url":"https://openreplay.com","github_url":"https://github.com/openreplay/openreplay","is_new":False,"kills_count":892,"created_at":"2024-02-15","active":True},
    {"id":"devtrack","name":"DevTrack","icon":"🐛","cat":"devtools","kills":"Jira","saving":"$84/mo","saving_yearly":1008,"desc":"Issue tracker for developers. Sprints, backlogs, Git integration, CI/CD status.","features":["Sprints & backlog","Git integration","CI/CD status","Custom workflows","Roadmap view","Time tracking","API","Webhooks"],"tags":["online","selfhost"],"users":"29.7k","stars":"21.3k","gen_time":"55s","deploy":"# Hosted free\nhttps://plane.so\n\n# Self-host\ndocker run -p 3000:3000 makeplane/plane","online_url":"https://plane.so","github_url":"https://github.com/makeplane/plane","is_new":False,"kills_count":3102,"created_at":"2024-01-05","active":True},
    {"id":"formcraft","name":"FormCraft","icon":"📋","cat":"devtools","kills":"Typeform","saving":"$25/mo","saving_yearly":300,"desc":"Beautiful forms with logic jumps, file uploads, payments and webhooks.","features":["Logic jumps","File uploads","Payments","Webhooks","Analytics","Custom themes","PDF export","Embed anywhere"],"tags":["online","selfhost"],"users":"14.3k","stars":"11.2k","gen_time":"33s","deploy":"# Hosted free\nhttps://formbricks.com\n\n# Self-host\ndocker run -p 3000:3000 formbricks/formbricks","online_url":"https://formbricks.com","github_url":"https://github.com/formbricks/formbricks","is_new":True,"kills_count":1204,"created_at":"2024-03-12","active":True},
]

# ─── AUTH DECORATOR ──────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ─────────────────────────────────────────────────────────────
# PUBLIC ROUTES
# ─────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tools")
def api_tools():
    data  = load_data()
    tools = [t for t in data["tools"] if t.get("active", True)]

    cat  = request.args.get("cat", "all")
    sort = request.args.get("sort", "popular")
    q    = request.args.get("q", "").lower().strip()
    tag  = request.args.get("tag", "")

    if cat and cat != "all":
        tools = [t for t in tools if t["cat"] == cat]
    if q:
        tools = [t for t in tools if q in t["name"].lower()
                 or q in t["kills"].lower() or q in t["desc"].lower()]
    if tag == "online":
        tools = [t for t in tools if "online" in t["tags"]]
    elif tag == "selfhost":
        tools = [t for t in tools if "selfhost" in t["tags"]]
    elif tag == "new":
        tools = [t for t in tools if t.get("is_new")]

    if sort == "newest":
        tools = sorted(tools, key=lambda t: t.get("created_at",""), reverse=True)
    elif sort == "savings":
        tools = sorted(tools, key=lambda t: t.get("saving_yearly", 0), reverse=True)
    else:
        tools = sorted(tools, key=lambda t: t.get("kills_count", 0), reverse=True)

    return jsonify({"tools": tools, "total": len(tools)})


@app.route("/api/stats")
def api_stats():
    data  = load_data()
    tools = [t for t in data["tools"] if t.get("active", True)]
    cats  = ["design","productivity","crm","devtools","communication","automation","analytics"]
    return jsonify({
        "total_tools":          len(tools),
        "total_kills":          sum(t.get("kills_count", 0) for t in tools),
        "total_savings_yearly": sum(t.get("saving_yearly", 0) for t in tools),
        "categories":           {c: sum(1 for t in tools if t["cat"] == c) for c in cats},
        "new_tools":            sum(1 for t in tools if t.get("is_new")),
        "pending_requests":     len([r for r in data["kill_requests"] if r["status"] == "queued"]),
    })


@app.route("/api/submit", methods=["POST"])
@app.route("/api/kill-request", methods=["POST"])
def api_kill_request():
    data = load_data()
    body = request.get_json(silent=True) or {}
    name = (body.get("name") or body.get("saas_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "Please enter the SaaS name."}), 400
    entry = {
        "id":          str(uuid.uuid4())[:8],
        "saas_name":   name,
        "email":       (body.get("email") or "").strip(),
        "github_url":  (body.get("github_url") or "").strip(),
        "online_url":  (body.get("online_url") or "").strip(),
        "description": (body.get("description") or "").strip(),
        "status":      "queued",
        "created_at":  datetime.utcnow().isoformat(),
        "votes":       1,
    }
    data["kill_requests"].append(entry)
    save_data(data)
    return jsonify({"ok": True, "message": f"'{name}' added to kill queue.",
                    "request": entry, "queue_position": len(data["kill_requests"])}), 201


@app.route("/api/kill-requests")
def api_kill_requests():
    data = load_data()
    reqs = sorted(data["kill_requests"], key=lambda r: r["votes"], reverse=True)
    return jsonify({"requests": reqs, "total": len(reqs)})


@app.route("/api/kill-request/<req_id>/vote", methods=["POST"])
def api_vote(req_id):
    data = load_data()
    req  = next((r for r in data["kill_requests"] if r["id"] == req_id), None)
    if not req:
        abort(404)
    req["votes"] += 1
    save_data(data)
    return jsonify({"success": True, "votes": req["votes"]})


# ─────────────────────────────────────────────────────────────
# ADMIN AUTH
# ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Wrong password."
    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# ─────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────

@app.route("/admin")
@admin_required
def admin_dashboard():
    data = load_data()
    tools = data["tools"]
    reqs  = sorted(data["kill_requests"], key=lambda r: r["votes"], reverse=True)
    stats = {
        "total":    len(tools),
        "active":   sum(1 for t in tools if t.get("active", True)),
        "inactive": sum(1 for t in tools if not t.get("active", True)),
        "pending":  sum(1 for r in reqs if r["status"] == "queued"),
        "done":     sum(1 for r in reqs if r["status"] == "done"),
    }
    return render_template("admin.html", tools=tools, requests=reqs, stats=stats)


# ─── ADD TOOL ────────────────────────────────────────────────
@app.route("/admin/tools/add", methods=["GET", "POST"])
@admin_required
def admin_add_tool():
    if request.method == "POST":
        data = load_data()
        f    = request.form
        tool = {
            "id":            f.get("id","").strip().lower().replace(" ","-") or str(uuid.uuid4())[:8],
            "name":          f.get("name","").strip(),
            "icon":          f.get("icon","🔧").strip(),
            "cat":           f.get("cat","devtools"),
            "kills":         f.get("kills","").strip(),
            "saving":        f.get("saving","").strip(),
            "saving_yearly": int(f.get("saving_yearly", 0) or 0),
            "desc":          f.get("desc","").strip(),
            "features":      [x.strip() for x in f.get("features","").split("\n") if x.strip()],
            "tags":          [x.strip() for x in f.get("tags","").split(",") if x.strip()],
            "users":         f.get("users","0").strip(),
            "stars":         f.get("stars","0").strip(),
            "gen_time":      f.get("gen_time","—"),
            "deploy":        f.get("deploy","").strip(),
            "online_url":    f.get("online_url","").strip(),
            "github_url":    f.get("github_url","").strip(),
            "is_new":        f.get("is_new") == "on",
            "kills_count":   int(f.get("kills_count", 0) or 0),
            "created_at":    datetime.utcnow().strftime("%Y-%m-%d"),
            "active":        True,
        }
        # check duplicate id
        if any(t["id"] == tool["id"] for t in data["tools"]):
            tool["id"] = tool["id"] + "-" + str(uuid.uuid4())[:4]
        data["tools"].append(tool)
        save_data(data)
        return redirect(url_for("admin_dashboard"))
    cats = ["design","productivity","crm","devtools","communication","automation","analytics"]
    return render_template("admin_tool_form.html", tool=None, cats=cats, action="Add")


# ─── EDIT TOOL ───────────────────────────────────────────────
@app.route("/admin/tools/<tool_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_tool(tool_id):
    data = load_data()
    tool = next((t for t in data["tools"] if t["id"] == tool_id), None)
    if not tool:
        abort(404)
    if request.method == "POST":
        f = request.form
        tool.update({
            "name":          f.get("name", tool["name"]).strip(),
            "icon":          f.get("icon", tool["icon"]).strip(),
            "cat":           f.get("cat", tool["cat"]),
            "kills":         f.get("kills", tool["kills"]).strip(),
            "saving":        f.get("saving", tool["saving"]).strip(),
            "saving_yearly": int(f.get("saving_yearly", tool["saving_yearly"]) or 0),
            "desc":          f.get("desc", tool["desc"]).strip(),
            "features":      [x.strip() for x in f.get("features","").split("\n") if x.strip()],
            "tags":          [x.strip() for x in f.get("tags","").split(",") if x.strip()],
            "users":         f.get("users", tool["users"]).strip(),
            "stars":         f.get("stars", tool["stars"]).strip(),
            "gen_time":      f.get("gen_time", tool["gen_time"]),
            "deploy":        f.get("deploy", tool["deploy"]).strip(),
            "online_url":    f.get("online_url", tool["online_url"]).strip(),
            "github_url":    f.get("github_url", tool["github_url"]).strip(),
            "is_new":        f.get("is_new") == "on",
            "kills_count":   int(f.get("kills_count", tool["kills_count"]) or 0),
        })
        save_data(data)
        return redirect(url_for("admin_dashboard"))
    cats = ["design","productivity","crm","devtools","communication","automation","analytics"]
    return render_template("admin_tool_form.html", tool=tool, cats=cats, action="Edit")


# ─── TOGGLE ACTIVE ───────────────────────────────────────────
@app.route("/admin/tools/<tool_id>/toggle", methods=["POST"])
@admin_required
def admin_toggle_tool(tool_id):
    data = load_data()
    tool = next((t for t in data["tools"] if t["id"] == tool_id), None)
    if not tool:
        abort(404)
    tool["active"] = not tool.get("active", True)
    save_data(data)
    return redirect(url_for("admin_dashboard"))


# ─── DELETE TOOL ─────────────────────────────────────────────
@app.route("/admin/tools/<tool_id>/delete", methods=["POST"])
@admin_required
def admin_delete_tool(tool_id):
    data = load_data()
    data["tools"] = [t for t in data["tools"] if t["id"] != tool_id]
    save_data(data)
    return redirect(url_for("admin_dashboard"))


# ─── MANAGE KILL REQUEST ─────────────────────────────────────
@app.route("/admin/requests/<req_id>/status", methods=["POST"])
@admin_required
def admin_request_status(req_id):
    data   = load_data()
    req    = next((r for r in data["kill_requests"] if r["id"] == req_id), None)
    if not req:
        abort(404)
    req["status"] = request.form.get("status", req["status"])
    save_data(data)
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/requests/<req_id>/delete", methods=["POST"])
@admin_required
def admin_delete_request(req_id):
    data = load_data()
    data["kill_requests"] = [r for r in data["kill_requests"] if r["id"] != req_id]
    save_data(data)
    return redirect(url_for("admin_dashboard"))


# ─── EXPORT / IMPORT JSON ────────────────────────────────────
@app.route("/admin/export")
@admin_required
def admin_export():
    data = load_data()
    from flask import Response
    return Response(json.dumps(data, indent=2, ensure_ascii=False),
                    mimetype="application/json",
                    headers={"Content-Disposition": "attachment;filename=killallsaas_data.json"})


# ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
