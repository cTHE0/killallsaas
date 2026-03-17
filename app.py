from flask import Flask, render_template, jsonify, request, abort
from datetime import datetime
import uuid

app = Flask(__name__)

# ─── DATA (swap with Postgres/Supabase in prod) ───────────────
TOOLS = [
    {"id":"pixelforge","name":"PixelForge","icon":"🎨","cat":"design","kills":"Adobe Photoshop","saving":"$55/mo","saving_yearly":660,"desc":"Full browser-based image editor. Layers, masks, filters, RAW support. Works like Photoshop — no install, no subscription.","features":["Layers & blend modes","Non-destructive filters","RAW support","Brush & selection tools","Color grading","Export PNG/JPG/WebP","Masks & clipping","Plugin support"],"tags":["online","design"],"users":"14.2k","stars":"9.1k","gen_time":"54s","deploy":"# Open right now\nhttps://photopea.com\n\n# Self-host\ndocker run -p 3000:3000 nicedoc/photopea","online_url":"https://photopea.com","github_url":"https://github.com/nicktindall/cyclon.p2p","is_new":False,"kills_count":1247,"created_at":"2024-01-15"},
    {"id":"designforge","name":"DesignForge","icon":"✏️","cat":"design","kills":"Figma","saving":"$45/editor/mo","saving_yearly":540,"desc":"Collaborative vector design tool. Real-time multiplayer, components, auto-layout, prototyping — all in the browser.","features":["Real-time collaboration","Vector editing","Components & variants","Auto-layout","Prototyping & flows","Asset export","Dark mode","REST API"],"tags":["online","selfhost"],"users":"19.8k","stars":"15.3k","gen_time":"63s","deploy":"# Launch online\nhttps://penpot.app\n\n# Self-host\ndocker run -p 3449:3449 penpotapp/frontend","online_url":"https://penpot.app","github_url":"https://github.com/penpot/penpot","is_new":True,"kills_count":2891,"created_at":"2024-03-01"},
    {"id":"drawpad","name":"DrawPad","icon":"🖊️","cat":"design","kills":"Miro / FigJam","saving":"$16/mo","saving_yearly":192,"desc":"Infinite collaborative whiteboard. Sticky notes, shapes, diagrams, real-time cursors. Runs in any browser.","features":["Infinite canvas","Real-time cursors","Sticky notes","Diagrams & shapes","Image embed","Export SVG/PNG","Guest access","Keyboard shortcuts"],"tags":["online","selfhost"],"users":"11.4k","stars":"8.7k","gen_time":"38s","deploy":"# Online now\nhttps://excalidraw.com\n\n# Self-host\ndocker run -p 80:80 excalidraw/excalidraw","online_url":"https://excalidraw.com","github_url":"https://github.com/excalidraw/excalidraw","is_new":False,"kills_count":743,"created_at":"2024-01-20"},
    {"id":"vidcut","name":"VidCut","icon":"🎬","cat":"design","kills":"Adobe Premiere","saving":"$55/mo","saving_yearly":660,"desc":"Browser-based video editor. Cut, trim, subtitles, transitions, color grading. No install needed.","features":["Multi-track timeline","Auto-subtitles AI","Color grading","Transitions & effects","Audio mixer","Export up to 4K","Stock footage","AI cut detection"],"tags":["online"],"users":"7.8k","stars":"5.2k","gen_time":"88s","deploy":"# Browser-based\nhttps://clideo.com\n\n# Desktop open source\nbrew install kdenlive","online_url":"https://clideo.com","github_url":"https://github.com/KDE/kdenlive","is_new":True,"kills_count":421,"created_at":"2024-03-10"},
    {"id":"slidecraft","name":"SlideCraft","icon":"📊","cat":"design","kills":"Canva Pro","saving":"$15/mo","saving_yearly":180,"desc":"Design tool for presentations, social media, and marketing materials. 500+ templates, brand kit.","features":["500+ templates","Brand kit","Drag & drop","Magic resize","Animations","PDF/PNG export","Team sharing","Custom fonts"],"tags":["online"],"users":"8.9k","stars":"4.8k","gen_time":"41s","deploy":"# Open source slides\nnpx slidev\n\n# Or self-host\ndocker run -p 3000:3000 glitchlab/slide","online_url":"https://pitch.com","github_url":"https://github.com/slidevjs/slidev","is_new":False,"kills_count":612,"created_at":"2024-02-05"},
    {"id":"opennote","name":"OpenNote","icon":"📝","cat":"productivity","kills":"Notion","saving":"$16/user/mo","saving_yearly":192,"desc":"All-in-one workspace. Notes, databases, kanban, wikis, docs. Full Notion replacement, self-hostable, your data stays yours.","features":["Rich text editor","Databases & views","Kanban boards","Team wiki","Page sharing","Import from Notion","Mobile apps","API access"],"tags":["online","selfhost"],"users":"34.6k","stars":"24.2k","gen_time":"48s","deploy":"# Hosted free\nhttps://appflowy.io\n\n# Self-host\ndocker run -p 8080:8080 appflowyinc/appflowy-cloud","online_url":"https://appflowy.io","github_url":"https://github.com/AppFlowy-IO/AppFlowy","is_new":False,"kills_count":4821,"created_at":"2024-01-01"},
    {"id":"gridbase","name":"GridBase","icon":"🗂️","cat":"productivity","kills":"Airtable","saving":"$24/mo","saving_yearly":288,"desc":"Spreadsheet meets database. Grid, kanban, gallery, calendar views. Automations, forms, API.","features":["Grid / Kanban / Gallery","Automations","Forms & surveys","Field relationships","API & webhooks","Import CSV/Excel","Formulas","Permissions"],"tags":["online","selfhost"],"users":"16.2k","stars":"12.8k","gen_time":"52s","deploy":"# Online\nhttps://nocodb.com\n\n# Self-host\ndocker run -p 8080:8080 nocodb/nocodb","online_url":"https://nocodb.com","github_url":"https://github.com/nocodb/nocodb","is_new":False,"kills_count":2341,"created_at":"2024-01-10"},
    {"id":"taskflow","name":"TaskFlow","icon":"✅","cat":"productivity","kills":"Asana / Monday","saving":"$30/mo","saving_yearly":360,"desc":"Project management with kanban, Gantt timeline, and list views. Subtasks, dependencies, time tracking.","features":["Kanban & list","Gantt timeline","Subtasks","Dependencies","Time tracking","Reports","Guest access","Mobile app"],"tags":["online","selfhost"],"users":"24.1k","stars":"19.6k","gen_time":"39s","deploy":"# Hosted free\nhttps://plane.so\n\n# Self-host\ndocker-compose up -d","online_url":"https://plane.so","github_url":"https://github.com/makeplane/plane","is_new":True,"kills_count":1987,"created_at":"2024-02-20"},
    {"id":"bookitfree","name":"BookItFree","icon":"📅","cat":"productivity","kills":"Calendly","saving":"$12/mo","saving_yearly":144,"desc":"Share your calendar link, let anyone book. Integrates with Google Calendar, Outlook. Customizable booking page.","features":["Availability rules","Booking page","Calendar sync","Email reminders","Round-robin","Group events","Payment collection","Embed widget"],"tags":["online","selfhost"],"users":"9.4k","stars":"7.2k","gen_time":"31s","deploy":"# Hosted free\nhttps://cal.com\n\n# Self-host\ndocker run -p 3000:3000 calcom/cal.com","online_url":"https://cal.com","github_url":"https://github.com/calcom/cal.com","is_new":False,"kills_count":891,"created_at":"2024-01-25"},
    {"id":"opencrm","name":"OpenCRM","icon":"🤝","cat":"crm","kills":"HubSpot","saving":"$800/mo","saving_yearly":9600,"desc":"Full CRM — pipeline management, contact enrichment, email sequences, analytics. HubSpot without the price tag.","features":["Contact management","Deal pipelines","Email sequences","Call tracking","Reports & analytics","Lead scoring","Web forms","REST API"],"tags":["online","selfhost"],"users":"9.8k","stars":"7.8k","gen_time":"91s","deploy":"# Hosted free\nhttps://twenty.com\n\n# Self-host\ndocker-compose up","online_url":"https://twenty.com","github_url":"https://github.com/twentyhq/twenty","is_new":True,"kills_count":634,"created_at":"2024-03-05"},
    {"id":"mailfree","name":"MailFree","icon":"📧","cat":"crm","kills":"Mailchimp","saving":"$35/mo","saving_yearly":420,"desc":"Email marketing platform. Drag-and-drop builder, automations, segmentation, A/B testing. Unlimited when self-hosted.","features":["Drag & drop builder","Automations","Segmentation","A/B testing","Analytics","Templates","Landing pages","SMTP delivery"],"tags":["online","selfhost"],"users":"18.1k","stars":"13.4k","gen_time":"46s","deploy":"# Self-host (unlimited)\ndocker run -d -p 9000:9000 \\\n  -e 'LISTMONK_db__host=db' \\\n  listmonk/listmonk:latest","online_url":"https://listmonk.app","github_url":"https://github.com/knadh/listmonk","is_new":False,"kills_count":1543,"created_at":"2024-01-18"},
    {"id":"salescraft","name":"SalesCraft","icon":"💼","cat":"crm","kills":"Salesforce","saving":"$300/mo","saving_yearly":3600,"desc":"Enterprise CRM with custom objects, workflow automation, email integration, and deep reporting.","features":["Custom objects","Workflow engine","Email sync","Analytics","Territory mgmt","Forecasting","Mobile app","1000+ integrations"],"tags":["online","selfhost"],"users":"5.6k","stars":"4.9k","gen_time":"110s","deploy":"# Self-host\ndocker run -p 8069:8069 \\\n  -e PASSWORD=admin \\\n  odoo:17","online_url":"https://odoo.com","github_url":"https://github.com/odoo/odoo","is_new":False,"kills_count":312,"created_at":"2024-02-01"},
    {"id":"devtrack","name":"DevTrack","icon":"🐛","cat":"devtools","kills":"Jira","saving":"$84/mo","saving_yearly":1008,"desc":"Issue tracker made for developers. Sprints, backlogs, Git integration, CI/CD status. Fast, no bloat.","features":["Sprints & backlog","Git integration","CI/CD status","Custom workflows","Roadmap view","Time tracking","API","Webhooks"],"tags":["online","selfhost"],"users":"29.7k","stars":"21.3k","gen_time":"55s","deploy":"# Hosted free\nhttps://plane.so\n\n# Self-host\ndocker run -p 3000:3000 makeplane/plane","online_url":"https://plane.so","github_url":"https://github.com/makeplane/plane","is_new":False,"kills_count":3102,"created_at":"2024-01-05"},
    {"id":"codeai","name":"CodeAI","icon":"👨‍💻","cat":"devtools","kills":"GitHub Copilot","saving":"$19/mo","saving_yearly":228,"desc":"AI code completion and review in your editor. 40+ languages. Runs locally — no data leaves your machine.","features":["AI completion","Code review","40+ languages","Local LLM (Ollama)","VS Code extension","Security scan","Refactoring","Doc generation"],"tags":["selfhost"],"users":"12.4k","stars":"11.1k","gen_time":"72s","deploy":"# Install Ollama + Continue\nbrew install ollama\ncurl -fsSL https://continue.dev/install | bash","online_url":"https://continue.dev","github_url":"https://github.com/continuedev/continue","is_new":True,"kills_count":987,"created_at":"2024-03-08"},
    {"id":"logwatcher","name":"LogWatcher","icon":"📈","cat":"devtools","kills":"Datadog","saving":"$300/mo","saving_yearly":3600,"desc":"Full observability: metrics, logs, traces, dashboards, alerting. Unlimited data when self-hosted.","features":["Metrics ingestion","Log aggregation","Distributed tracing","Dashboards","Alerting","APM","Synthetic monitoring","No data limits"],"tags":["online","selfhost"],"users":"8.2k","stars":"7.1k","gen_time":"95s","deploy":"# Self-host Grafana stack\ndocker-compose up -d \\\n  grafana prometheus loki tempo","online_url":"https://grafana.com","github_url":"https://github.com/grafana/grafana","is_new":False,"kills_count":521,"created_at":"2024-01-30"},
    {"id":"formcraft","name":"FormCraft","icon":"📋","cat":"devtools","kills":"Typeform","saving":"$25/mo","saving_yearly":300,"desc":"Beautiful forms with logic jumps, file uploads, payments and webhooks. One-click embed anywhere.","features":["Logic jumps","File uploads","Payments","Webhooks","Analytics","Custom themes","PDF export","Embed anywhere"],"tags":["online","selfhost"],"users":"14.3k","stars":"11.2k","gen_time":"33s","deploy":"# Hosted free\nhttps://formbricks.com\n\n# Self-host\ndocker run -p 3000:3000 formbricks/formbricks","online_url":"https://formbricks.com","github_url":"https://github.com/formbricks/formbricks","is_new":True,"kills_count":1204,"created_at":"2024-03-12"},
    {"id":"freechat","name":"FreeChat","icon":"💬","cat":"communication","kills":"Slack","saving":"$8/user/mo","saving_yearly":96,"desc":"Team messaging with channels, threads, video calls, screen sharing, and full-text search.","features":["Channels & threads","Video calls","Screen sharing","File sharing","Full-text search","Bots & apps","Mobile apps","E2E encryption"],"tags":["online","selfhost"],"users":"44.8k","stars":"36.2k","gen_time":"44s","deploy":"# Docker\ndocker run --rm \\\n  -e ROOT_URL=http://localhost \\\n  -p 3000:3000 rocket.chat","online_url":"https://rocket.chat","github_url":"https://github.com/RocketChat/Rocket.Chat","is_new":False,"kills_count":5214,"created_at":"2024-01-01"},
    {"id":"meetfree","name":"MeetFree","icon":"📹","cat":"communication","kills":"Zoom","saving":"$15/mo","saving_yearly":180,"desc":"Video conferencing for up to 100 people. Recording, waiting room, breakout rooms. No app needed.","features":["HD video & audio","Screen sharing","Recording","Waiting room","Breakout rooms","Polls","Whiteboard","No app needed"],"tags":["online"],"users":"21.6k","stars":"16.8k","gen_time":"58s","deploy":"# Use now — no account\nhttps://meet.jit.si\n\n# Self-host\ndocker-compose up","online_url":"https://meet.jit.si","github_url":"https://github.com/jitsi/jitsi-meet","is_new":False,"kills_count":2876,"created_at":"2024-01-12"},
    {"id":"signfree","name":"SignFree","icon":"✍️","cat":"communication","kills":"DocuSign","saving":"$45/mo","saving_yearly":540,"desc":"Send documents for e-signature. Templates, audit trail, bulk send. Legally binding in 40+ countries.","features":["E-signatures","Templates","Audit trail","Bulk send","In-person signing","Mobile app","PDF editor","API access"],"tags":["online","selfhost"],"users":"9.1k","stars":"7.4k","gen_time":"61s","deploy":"# Hosted free\nhttps://docuseal.com\n\n# Self-host\ndocker run -p 3000:3000 docuseal/docuseal","online_url":"https://docuseal.com","github_url":"https://github.com/docusealco/docuseal","is_new":True,"kills_count":743,"created_at":"2024-03-15"},
    {"id":"autoflow","name":"AutoFlow","icon":"⚡","cat":"automation","kills":"Zapier","saving":"$49/mo","saving_yearly":588,"desc":"Visual workflow automation with 400+ integrations. Build complex multi-step workflows without code.","features":["400+ integrations","Visual builder","Branches & conditions","Error handling","Webhooks","Cron jobs","Data transform","Self-hosted"],"tags":["online","selfhost"],"users":"26.4k","stars":"21.7k","gen_time":"57s","deploy":"# Hosted free tier\nhttps://n8n.io\n\n# Self-host\ndocker run -p 5678:5678 n8nio/n8n","online_url":"https://n8n.io","github_url":"https://github.com/n8n-io/n8n","is_new":False,"kills_count":3421,"created_at":"2024-01-08"},
    {"id":"makerbot","name":"MakerBot","icon":"🤖","cat":"automation","kills":"Make / Integromat","saving":"$29/mo","saving_yearly":348,"desc":"Drag-and-drop automation scenarios. Real-time execution, visual data mapping, error recovery.","features":["Visual scenarios","Data mapping","Real-time exec","Error recovery","Webhooks","Scheduler","Team sharing","REST API"],"tags":["online","selfhost"],"users":"12.1k","stars":"9.6k","gen_time":"49s","deploy":"# Self-host\ndocker run -p 8080:8080 \\\n  activepieces/activepieces","online_url":"https://activepieces.com","github_url":"https://github.com/activepieces/activepieces","is_new":False,"kills_count":1123,"created_at":"2024-02-10"},
    {"id":"statsopen","name":"StatsOpen","icon":"📊","cat":"analytics","kills":"Google Analytics","saving":"privacy","saving_yearly":0,"desc":"Privacy-first web analytics. No cookies, GDPR compliant, real-time dashboard. Script < 1KB.","features":["No cookies","GDPR / CCPA","Real-time","Custom events","Funnels","UTM tracking","Goals","Public dashboards"],"tags":["online","selfhost"],"users":"41.3k","stars":"31.8k","gen_time":"29s","deploy":"# Hosted free (10k pv)\nhttps://plausible.io\n\n# Self-host (unlimited)\ndocker run -p 8000:8000 plausible/analytics","online_url":"https://plausible.io","github_url":"https://github.com/plausible/analytics","is_new":False,"kills_count":6234,"created_at":"2024-01-01"},
    {"id":"heatmapper","name":"HeatMapper","icon":"🔥","cat":"analytics","kills":"Hotjar","saving":"$99/mo","saving_yearly":1188,"desc":"Session recording, heatmaps, click maps, funnel analysis. Understand what users actually do. GDPR safe.","features":["Session recording","Heatmaps","Click maps","Funnels","Rage click detection","Surveys","A/B testing","GDPR safe"],"tags":["online","selfhost"],"users":"8.1k","stars":"6.4k","gen_time":"67s","deploy":"# Self-host\ndocker-compose up -d","online_url":"https://openreplay.com","github_url":"https://github.com/openreplay/openreplay","is_new":False,"kills_count":892,"created_at":"2024-02-15"},
    {"id":"splittest","name":"SplitTest","icon":"🔬","cat":"analytics","kills":"Optimizely","saving":"$200/mo","saving_yearly":2400,"desc":"A/B testing and feature flags. Run experiments, measure impact, gradual rollouts. Developer-friendly SDK.","features":["A/B testing","Feature flags","Gradual rollouts","Statistical sig.","Multi-variate","Segmentation","SDK (JS/Python/Go)","Self-hosted"],"tags":["online","selfhost"],"users":"5.7k","stars":"4.6k","gen_time":"71s","deploy":"# Hosted free\nhttps://growthbook.io\n\n# Self-host\ndocker run -p 3000:3000 growthbook/growthbook","online_url":"https://growthbook.io","github_url":"https://github.com/growthbook/growthbook","is_new":True,"kills_count":412,"created_at":"2024-03-18"},
]

KILL_REQUESTS = []

# ─── ROUTES ──────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/tools")
def api_tools():
    cat  = request.args.get("cat", "all")
    sort = request.args.get("sort", "popular")
    q    = request.args.get("q", "").lower().strip()
    tag  = request.args.get("tag", "")
    tools = list(TOOLS)
    if cat and cat != "all":
        tools = [t for t in tools if t["cat"] == cat]
    if q:
        tools = [t for t in tools if q in t["name"].lower() or q in t["kills"].lower() or q in t["desc"].lower()]
    if tag == "online":
        tools = [t for t in tools if "online" in t["tags"]]
    elif tag == "selfhost":
        tools = [t for t in tools if "selfhost" in t["tags"]]
    elif tag == "new":
        tools = [t for t in tools if t["is_new"]]
    if sort == "newest":
        tools = sorted(tools, key=lambda t: t["created_at"], reverse=True)
    elif sort == "savings":
        tools = sorted(tools, key=lambda t: t["saving_yearly"], reverse=True)
    else:
        tools = sorted(tools, key=lambda t: t["kills_count"], reverse=True)
    return jsonify({"tools": tools, "total": len(tools)})

@app.route("/api/tools/<tool_id>")
def api_tool_detail(tool_id):
    tool = next((t for t in TOOLS if t["id"] == tool_id), None)
    if not tool:
        abort(404)
    return jsonify(tool)

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "total_tools": len(TOOLS),
        "total_kills": sum(t["kills_count"] for t in TOOLS),
        "total_savings_yearly": sum(t["saving_yearly"] for t in TOOLS),
        "categories": {c: sum(1 for t in TOOLS if t["cat"] == c) for c in ["design","productivity","crm","devtools","communication","automation","analytics"]},
        "new_tools": sum(1 for t in TOOLS if t["is_new"]),
    })

@app.route("/api/kill-request", methods=["POST"])
def api_kill_request():
    data = request.get_json(silent=True) or {}
    name = (data.get("saas_name") or "").strip()
    if not name:
        return jsonify({"error": "saas_name required"}), 400
    entry = {"id": str(uuid.uuid4())[:8], "saas_name": name, "email": data.get("email",""), "status": "queued", "created_at": datetime.utcnow().isoformat(), "votes": 1}
    KILL_REQUESTS.append(entry)
    return jsonify({"success": True, "message": f"'{name}' added to kill queue.", "request": entry, "queue_position": len(KILL_REQUESTS)}), 201

@app.route("/api/kill-requests")
def api_kill_requests():
    return jsonify({"requests": sorted(KILL_REQUESTS, key=lambda r: r["votes"], reverse=True), "total": len(KILL_REQUESTS)})

@app.route("/api/kill-request/<req_id>/vote", methods=["POST"])
def api_vote(req_id):
    req = next((r for r in KILL_REQUESTS if r["id"] == req_id), None)
    if not req:
        abort(404)
    req["votes"] += 1
    return jsonify({"success": True, "votes": req["votes"]})

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, port=5000)
