import os
import re
import feedparser
import socket
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify, send_from_directory

# --- KONFIGURATION ---
socket.setdefaulttimeout(10)
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANZ_DIR = "/root/lanz" 
ENIGMA_IP = "192.168.0.25"
RSS_URL = "https://www.tagesschau.de/infoservices/alle-meldungen-100~rss2.xml"
BG_FILENAME = "wald2.jpg"

# Deine Mediathek-Feeds
MEDIATHEK_FEEDS = [
    ("12", "Wiso.m3u8", "https://mediathekviewweb.de/feed?query=!ZDF%20wiso%20%3E20W"),
    ("40", "Neuseeland.m3u8", "https://mediathekviewweb.de/feed?query=neuseeland"),
    ("50", "ZDF.m3u8","https://mediathekviewweb.de/feed?query=%22ZDF%22%20%3E10%20%3C130&future=false"),
    ("2",  "Nachrichten.m3u8", "http://www.zdf.de/rss/podcast/video/zdf/nachrichten/heute-19-uhr"),
    ("5",  "Lanz.m3u8", "https://mediathekviewweb.de/feed?query=!ZDF%20lanz%20%3E40"),
    ("40", "H-Lesch.m3u8", "https://mediathekviewweb.de/feed?query=harald%20lesch"),
    ("40", "Weihnachten.m3u8","https://mediathekviewweb.de/feed?query=weihnachten%20%3E50"),
    ("40", "ARTE-Geschichte.m3u8","https://mediathekviewweb.de/feed?query=!ARTE.de%20Geschichte"),
    ("10", "nano.m3u8", "https://mediathekviewweb.de/feed?query=!SRF%20nano&everywhere=true&future=false"),
    ("10", "Wunderschoen.m3u8", "https://mediathekviewweb.de/feed?query=!WDR%20Wundersch%C3%B6n"),
    ("40", "Winterzauber.m3u8","https://mediathekviewweb.de/feed?query=winterzauber%20%3E28"),
    ("20", "ARTE_Wissenschaft.m3u8", "https://mediathekviewweb.de/feed?query=!ARTE%20Wissenschaft%20%3E30"),
    ("30", "ZDF_filme.m3u8", "https://mediathekviewweb.de/feed?query=%09Spielfilm-Highlights"),
    ("30", "Regenwald.m3u8","https://mediathekviewweb.de/feed?query=Regenwald%20%3E30"),
    ("30", "Terrax.m3u8","https://mediathekviewweb.de/feed?query=Terra%20X%20%3E30"),
    ("30", "Norwegen.m3u8","https://mediathekviewweb.de/feed?query=*norwegen%20fjorde%20%3E30"),
    ("5",  "Tagesschau.m3u8","https://mediathekviewweb.de/feed?query=!ARD%20Tagesschau"),
    ("30", "Pilze.m3u8","https://mediathekviewweb.de/feed?query=pilze%20%3E33"),
    ("5",  "Wetter_8.m3u8","https://mediathekviewweb.de/feed?query=Wetter%20vor%20acht"),
    ("20", "Winterhütten.m3u8","https://mediathekviewweb.de/feed?query=winterh%C3%BCttengeschichte"),
    ("5",  "Hessenschau.m3u8","https://mediathekviewweb.de/feed?query=hessenschau"),
    ("20", "tagesschau24.m3u8","https://mediathekviewweb.de/feed?query=tagesschau24"),
    ("30", "Japan.m3u8","https://mediathekviewweb.de/feed?query=Japan%20%3E35"),
    ("10", "Maybrit.m3u8","https://mediathekviewweb.de/feed?query=maybrit%20illner"),
    ("40", "Marktbericht.m3u8","https://mediathekviewweb.de/feed?query=Update%20Wirtschaft"),
    ("30", "Unterwegs.m3u8","https://mediathekviewweb.de/feed?query=!3sat%20unterwegs%20reise"),
    ("30", "Bäume.m3u8","https://mediathekviewweb.de/feed?query=B%C3%A4ume%20%3E28"),
    ("30", "Boerse_8.m3u8","https://mediathekviewweb.de/feed?query=Wirtschaft%20vor%20acht"),
    ("50", "Hessen.m3u8","https://mediathekviewweb.de/feed?query=!HR&page=2"),
    ("10", "Kulturzeit.m3u8","https://mediathekviewweb.de/feed?query=!3sat%20kulturzeit"),
    ("30", "Duell-der-Gartenprofis.m3u8","https://mediathekviewweb.de/feed?query=Duell%20der%20Gartenprofis"),
    ("30", "SWR.m3u8","https://mediathekviewweb.de/feed?query=!SWR%20Dokumentation%20%26%20Reportage"),
    ("50", "China.m3u8","https://mediathekviewweb.de/feed?query=%2Bchina%20%3E30"),
    ("20", "Weltspiegel.m3u8","https://mediathekviewweb.de/feed?query=weltspiegel&everywhere=true&future=false"),
    ("20", "Fruehling.m3u8","https://mediathekviewweb.de/feed?query=!ZDF%20Fr%C3%BChling&everywhere=true&future=false"),
    ("20", "Geirangerfjord.m3u8","https://mediathekviewweb.de/feed?query=Geirangerfjord&everywhere=true&future=false"),
    ("30", "Schottland.m3u8","https://mediathekviewweb.de/feed?query=Schottland%20%3E30&everywhere=true&future=false"),
    ("30", "Highlands.m3u8","https://mediathekviewweb.de/feed?query=%20Highlands&everywhere=true&future=false"),
    ("15", "Maisberger.m3u8","https://mediathekviewweb.de/feed?query=maischberger"),
    ("30", "NDR-Story.m3u8","https://mediathekviewweb.de/feed?query=ndr%20story"),
    ("30", "Endeckung-der-Welt.m3u8","https://mediathekviewweb.de/feed?query=Entdeckung%20der%20Welt%20-%20Na&page=3")
]

EXTRA_LINKS = [
    {"text": "ARD-Mediathek", "url": "http://192.168.0.61:8123/api/webhook/-0660dPc_qG4UXzgu9KL8D8qy"},
    {"text": "Netflix", "url": "http://192.168.0.61:8123/api/webhook/-IHLdJjCsJqBPGWM5Ycb5tLjQ"},
    {"text": "YouTube", "url": "http://192.168.0.61:8123/api/webhook/-4qC2GjceXHLwtZA_atJKAOkr"},
    {"text": "HAOS", "url": "http://192.168.0.61:8123/dashboard-watch/0?homescreen=1"}
]

ENIGMA_CHANNELS = [
    {"name": "Das Erste HD", "url": f"http://{ENIGMA_IP}:8001/1:0:19:283D:3FB:1:C00000:0:0:0:", "logo": f"http://{ENIGMA_IP}/picon/1_0_19_283D_3FB_1_C00000_0_0_0.png"},
    {"name": "ZDF HD", "url": f"http://{ENIGMA_IP}:8001/1:0:19:2B66:3F3:1:C00000:0:0:0:", "logo": f"http://{ENIGMA_IP}/picon/1_0_19_2B66_3F3_1_C00000_0_0_0.png"},
    {"name": "3sat HD", "url": f"http://{ENIGMA_IP}:8001/1:0:19:2B8E:3F2:1:C00000:0:0:0:", "logo": f"http://{ENIGMA_IP}/picon/1_0_19_2B8E_3F2:1:C00000_0_0_0.png"}
]

# --- PLAYLIST GENERATOR ---

def update_mediathek_files():
    if not os.path.exists(LANZ_DIR): os.makedirs(LANZ_DIR)
    for max_entries, filename, url in MEDIATHEK_FEEDS:
        try:
            feed = feedparser.parse(url)
            items = []
            for entry in feed.entries:
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    t_low = entry.title.lower()
                    if any(x in t_low for x in ["gebärdensprache", "trailer", "audiodeskription", "untertitel"]): continue
                    pub_date = entry.get('published_parsed', None)
                    date_str = datetime(*pub_date[:6]).strftime('%m-%y') if pub_date else "??-??"
                    items.append({'title': f"{date_str} {entry.title}", 'url': entry.enclosures[0].href})
                    if len(items) >= int(max_entries): break
            with open(os.path.join(LANZ_DIR, filename), 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for item in items: f.write(f"#EXTINF:-1,{item['title']}\n{item['url']}\n")
        except: pass

# --- UI TEMPLATE ---

STYLE = f'''
<style>
    * {{ scrollbar-width: none; -ms-overflow-style: none; }}
    *::-webkit-scrollbar {{ display: none; }}

    body {{ font-family: 'Segoe UI', sans-serif; background: url('/background.jpg') no-repeat center center fixed; background-size: cover; color: white; margin: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}
    .overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.35); z-index: -1; }}

    .header-section {{ padding: 10px 25px; background: rgba(0,0,0,0.5); display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); }}
    #clock {{ font-size: 38px; font-weight: bold; color: #007bff; }}
    
    .btn-group {{ display: flex; gap: 10px; }}
    .btn {{ background: #444; color: white; border: 1px solid #666; padding: 7px 16px; border-radius: 20px; cursor: pointer; font-weight: bold; font-size: 13px; transition: 0.2s; }}
    .btn.active {{ background: #007bff; border-color: #00bfff; }}
    .btn-refresh {{ background: #28a745; border-color: #1e7e34; }}
    .btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

    .ticker-wrap {{ background: rgba(0,0,0,0.5); padding: 6px 0; overflow: hidden; border-bottom: 1px solid rgba(255,255,255,0.05); }}
    .ticker {{ display: inline-block; white-space: nowrap; padding-left: 100%; animation: marquee 420s linear infinite; font-size: 24px; color: #ffcc00; }}
    @keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-200%); }} }}

    .history-bar {{ background: rgba(0,0,0,0.7); padding: 10px 25px; display: flex; align-items: center; gap: 12px; overflow-x: auto; white-space: nowrap; border-bottom: 1px solid rgba(255,255,255,0.1); box-shadow: inset -20px 0 20px -20px rgba(0,0,0,0.5); }}
    .history-label {{ font-size: 11px; color: #888; text-transform: uppercase; margin-right: 5px; flex-shrink: 0; }}
    .history-item {{ font-size: 14px; color: #00ffcc; text-decoration: none; background: rgba(255,255,255,0.1); padding: 5px 15px; border-radius: 20px; border: 1px solid rgba(0,255,204,0.2); flex-shrink: 0; transition: 0.2s; }}
    .history-item:hover {{ background: rgba(0,255,204,0.1); }}

    .main-container {{ display: flex; flex: 1; overflow: hidden; }}
    .sidebar {{ width: 210px; background: rgba(0, 0, 0, 0.3); overflow-y: auto; border-right: 1px solid rgba(255,255,255,0.1); padding: 15px; }}
    .sidebar h2 {{ font-size: 12px; color: #888; letter-spacing: 1px; margin-bottom: 15px; }}
    .sidebar .card {{ background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; margin-bottom: 8px; cursor: pointer; font-size: 14px; transition: 0.2s; border: 1px solid transparent; }}
    .sidebar .card:hover {{ background: rgba(255,255,255,0.1); }}
    .sidebar .card.active {{ border-color: #007bff; background: rgba(0, 123, 255, 0.2); }}
    
    .content-area {{ flex: 1; overflow-y: auto; padding: 25px; scroll-behavior: smooth; }}
    .tv-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(95px, 1fr)); gap: 12px; margin-bottom: 40px; }}
    .tv-card {{ background: rgba(255,255,255,0.06); border-radius: 10px; padding: 10px; text-align: center; border: 1px solid rgba(255,255,255,0.1); transition: 0.2s; }}
    .tv-card:hover {{ border-color: #007bff; transform: translateY(-2px); }}
    .tv-card img {{ width: 65px; height: 40px; object-fit: contain; }}

    .list-item {{ background: rgba(0,0,0,0.45); padding: 15px; border-radius: 10px; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; border-left: 5px solid #007bff; transition: 0.2s; }}
    .list-item:hover {{ background: rgba(0,0,0,0.6); }}
    .list-item-link {{ text-decoration: none; color: white; display: block; }}
    
    h2 {{ font-size: 15px; color: #007bff; text-transform: uppercase; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; }}
    .back-btn {{ background: rgba(255,255,255,0.1); border: none; color: white; padding: 6px 14px; border-radius: 5px; cursor: pointer; font-weight: bold; }}
</style>
'''

@app.route('/')
def index():
    m3u_files = sorted([f for f in os.listdir(LANZ_DIR) if f.endswith('.m3u8')])
    news = " +++ ".join([item.title for item in feedparser.parse(RSS_URL).entries[:15]])
    tv_html = "".join([f'<a href="{c["url"]}" class="tv-card main-link"><img src="{c["logo"]}"></a>' for c in ENIGMA_CHANNELS])
    sidebar_html = "".join([f'<div class="card" onclick="loadPlaylist(\'{f}\', this)">📂 {f.replace(".m3u8","")}</div>' for f in m3u_files])
    extras_html = "".join([f'<a href="{e["url"]}" class="extra-link main-link" style="color:white;margin-right:20px;text-decoration:none;font-size:18px;">{e["text"]}</a>' for e in EXTRA_LINKS])

    return render_template_string(f'''
    <!DOCTYPE html><html><head>
        <meta charset="UTF-8">
        <title>ROOT HOME</title>
        <link rel="icon" href="https://cdn-icons-png.flaticon.com/512/716/716429.png">
        {STYLE}
    </head>
    <body>
        <div class="overlay"></div>
        <div class="header-section">
            <h1 style="margin:0; font-size: 24px; font-weight: 300; letter-spacing: 2px;">ROOT <span style="font-weight: 800; color: #007bff;">HUB</span></h1>
            <div class="btn-group">
                <button id="refreshBtn" class="btn btn-refresh" onclick="refreshMediathek()">MEDIATHEK LADEN ↻</button>
                <button id="targetBtn" class="btn active" onclick="toggleTarget()">MODUS: NEUER TAB ↗</button>
            </div>
            <div id="clock">--:--</div>
        </div>
        <div class="ticker-wrap"><div class="ticker">+++ {news} +++</div></div>
        <div class="history-bar" id="historyBar"></div>
        <div class="main-container">
            <div class="sidebar"><h2>SYSTEM MEDIATHEK</h2>{sidebar_html}</div>
            <div class="content-area" id="contentArea">
                <div id="tv-section"><h2>LIVE TV STREAM</h2><div class="tv-grid">{tv_html}</div></div>
                <div id="playlist-results" style="display:none; margin-bottom: 40px;"></div>
                <div id="extras-section"><h2>WEB LINKS & APPS</h2><div style="background:rgba(0,0,0,0.2);padding:20px;border-radius:10px;">{extras_html}</div></div>
            </div>
        </div>
        <script>
            let openInNewTab = true;
            let history = JSON.parse(localStorage.getItem('tvHistory') || '[]');

            function updateClock() {{
                document.getElementById('clock').innerHTML = new Date().toLocaleTimeString('de-DE', {{hour:'2-digit',minute:'2-digit'}});
            }}
            setInterval(updateClock, 1000); updateClock();

            function refreshMediathek() {{
                const btn = document.getElementById('refreshBtn');
                btn.innerHTML = "WIRD AKTUALISIERT..."; btn.disabled = true;
                fetch('/api/refresh').then(() => location.reload());
            }}

            function toggleTarget() {{
                openInNewTab = !openInNewTab;
                const btn = document.getElementById('targetBtn');
                btn.innerHTML = openInNewTab ? "MODUS: NEUER TAB ↗" : "MODUS: GLEICHER TAB";
                btn.classList.toggle('active', openInNewTab);
                updateLinkTargets();
            }}

            function updateLinkTargets() {{
                document.querySelectorAll('.main-link').forEach(a => a.target = openInNewTab ? "_blank" : "_self");
            }}

            function addToHistory(title, url) {{
                history = history.filter(item => item.url !== url);
                history.unshift({{title, url}});
                if(history.length > 10) history.pop();
                localStorage.setItem('tvHistory', JSON.stringify(history));
                renderHistory();
            }}

            function renderHistory() {{
                const bar = document.getElementById('historyBar');
                if (history.length === 0) {{ bar.style.display = 'none'; return; }}
                bar.style.display = 'flex';
                const items = history.map(item => `<a href="${{item.url}}" class="history-item main-link">${{item.title}}</a>`).join('');
                bar.innerHTML = '<span class="history-label">Zuletzt gesehen:</span>' + items;
                updateLinkTargets();
            }}

            function loadPlaylist(filename, element) {{
                document.querySelectorAll('.sidebar .card').forEach(c => c.classList.remove('active'));
                element.classList.add('active');
                const res = document.getElementById('playlist-results');
                res.style.display = 'block'; res.innerHTML = "<h2>Inhalt wird geladen...</h2>";
                fetch('/api/playlist/' + filename).then(r => r.json()).then(data => {{
                    let html = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:15px;">
                                <h2 style="margin:0;">📂 ${{filename.replace(".m3u8","").toUpperCase()}}</h2>
                                <button onclick="closePlaylist()" class="back-btn">SCHLIESSEN ✖</button></div>`;
                    data.forEach(i => {{
                        html += `<a href="${{i.url}}" class="list-item-link main-link" onclick="addToHistory('${{i.title.replace(/'/g,"")}}','${{i.url}}')">
                                    <div class="list-item"><span>${{i.title}}</span><b style="color:#007bff">JETZT ABSPIELEN ▶</b></div></a>`;
                    }});
                    res.innerHTML = html; updateLinkTargets();
                    res.scrollIntoView({{behavior:'smooth', block:'start'}});
                }});
            }}

            function closePlaylist() {{
                document.getElementById('playlist-results').style.display = 'none';
                document.querySelectorAll('.sidebar .card').forEach(c => c.classList.remove('active'));
                document.getElementById('contentArea').scrollTo({{top:0, behavior:'smooth'}});
            }}

            renderHistory(); updateLinkTargets();
        </script>
    </body></html>
    ''')

@app.route('/api/playlist/<filename>')
def api_playlist(filename):
    path = os.path.join(LANZ_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*)', content)
    return jsonify([{'title': t.strip(), 'url': u.strip()} for t, u in matches])

@app.route('/api/refresh')
def api_refresh():
    update_mediathek_files()
    return jsonify({"status": "done"})

@app.route('/background.jpg')
def background():
    return send_from_directory(BASE_DIR, BG_FILENAME)

if __name__ == '__main__':
    # Startet Mediathek-Update im Hintergrund
    threading.Thread(target=update_mediathek_files).start()
    app.run(host='0.0.0.0', port=5000, debug=False)

