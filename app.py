from flask import Flask, request, jsonify, send_file
import uuid, json
import os

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MC Manifest Generator Pro</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <style>
        :root {
            --bg-grad: radial-gradient(circle at top, #1e1b4b, #020617);
            --card-bg: rgba(30, 41, 59, 0.8);
            --text-main: #ffffff;
            --text-sub: #a5b4fc;
            --border: rgba(255,255,255,0.1);
            --input-bg: #020617;
            --p-color: #7c3aed;
            --s-color: #22d3ee;
            --glow-op: 0.5;
        }
        body.light-theme { --bg-grad: #f1f5f9; --card-bg: #ffffff; --text-main: #0f172a; --text-sub: #475569; --border: #e2e8f0; --input-bg: #f8fafc; --p-color: #4f46e5; --s-color: #0891b2; --glow-op: 0; }
        body.dark-theme { --bg-grad: #020617; --card-bg: #0f172a; --text-main: #f8fafc; --text-sub: #94a3b8; --border: #1e293b; --input-bg: #000000; --glow-op: 0; }
        body { margin:0; font-family: 'Segoe UI', sans-serif; background: var(--bg-grad); color: var(--text-main); min-height: 100vh; display: flex; align-items: center; justify-content: center; transition: 0.3s; }
        .app { width: 100%; max-width: 450px; padding: 20px; position: relative; }
        .menu-btn { position: fixed; top: 20px; right: 20px; cursor: pointer; z-index: 100; padding: 10px; background: var(--card-bg); border-radius: 10px; border: 1px solid var(--border); }
        .menu-btn div { width: 25px; height: 3px; background: var(--s-color); margin: 5px 0; border-radius: 2px; }
        .sidebar { position: fixed; top: 0; right: -250px; width: 200px; height: 100%; background: var(--card-bg); backdrop-filter: blur(20px); padding: 60px 20px; transition: 0.4s; z-index: 90; border-left: 1px solid var(--border); }
        .sidebar.active { right: 0; }
        .theme-opt { display: block; width: 100%; padding: 12px; margin-bottom: 10px; border: 1px solid var(--border); background: var(--input-bg); color: var(--text-main); border-radius: 10px; cursor: pointer; text-align: left; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h2 { margin: 0; font-size: 22px; background: linear-gradient(90deg, #c084fc, var(--s-color)); -webkit-background-clip: text; color: transparent; }
        .card { background: var(--card-bg); backdrop-filter: blur(15px); padding: 20px; border-radius: 20px; border: 1px solid var(--border); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
        .input-group { margin-bottom: 12px; }
        label { display: block; font-size: 11px; color: var(--text-sub); margin-bottom: 5px; font-weight: bold; }
        input, select { width: 100%; padding: 10px; border-radius: 10px; border: 1px solid var(--border); background: var(--input-bg); color: var(--text-main); font-size: 14px; box-sizing: border-box; }
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        button { padding: 12px; border: none; border-radius: 12px; background: linear-gradient(135deg, var(--p-color), var(--s-color)); font-weight: bold; color: white; cursor: pointer; font-size: 13px; }
        pre { background: #000; padding: 15px; border-radius: 10px; font-size: 12px; color: #38bdf8; overflow: auto; max-height: 180px; border: 1px solid #1e293b; margin-top: 10px;}
        #icon-preview { width: 64px; height: 64px; border-radius: 8px; border: 2px solid var(--s-color); object-fit: cover; display: none; margin: 10px auto; }
        .footer { text-align: center; margin-top: 20px; font-size: 11px; color: var(--text-sub); line-height: 1.6; }
        .highlight { color: var(--s-color); font-weight: bold; }
        .link-box a { color: var(--s-color); text-decoration: underline; font-weight: bold; }
    </style>
</head>
<body class="neon-theme">
<div class="menu-btn" onclick="toggleMenu()"><div></div><div></div><div></div></div>
<div class="sidebar" id="sidebar">
    <h4>Select Theme</h4>
    <button class="theme-opt" onclick="setTheme('neon')">✨ Neon Mode</button>
    <button class="theme-opt" onclick="setTheme('dark')">🌙 Dark Mode</button>
    <button class="theme-opt" onclick="setTheme('light')">☀️ Light Mode</button>
</div>
<div class="app">
    <div class="header"><h2>MC Manifest Generator ⚙️</h2></div>
    <div class="card">
        <div class="input-group"><label>Pack Icon</label><input type="file" id="icon-input" accept="image/*" onchange="processIcon()"><img id="icon-preview"></div>
        <div class="input-group"><label>Min Engine Version</label>
            <select id="engine" onchange="liveUpdate()">
                <option value="1,17,0">1.17.0</option><option value="1,21,0">1.21.0</option>
                <option value="1,26,3" selected>1.26.3 (Latest)</option>
            </select>
        </div>
        <div class="input-group"><label>Pack Name</label><input id="name" placeholder="Name..." oninput="liveUpdate()"></div>
        <div class="input-group"><label>Description</label><input id="desc" placeholder="Desc..." oninput="liveUpdate()"></div>
        <pre id="preview"></pre>
        <div class="btn-group"><button onclick="handleDownload()">Download</button><button onclick="copyJSON()">Copy Code</button></div>
    </div>
    <div class="footer">
        <div>Make by <span class="highlight">Probfix</span> & <span class="highlight">AI partner⚡</span></div>
        <div class="link-box">Need pack.mcmeta for Java? <a href="#" target="_blank">Click here</a></div>
    </div>
</div>
<canvas id="canvas" width="128" height="128" style="display:none;"></canvas>
<script>
let currentJSON = null; let iconBlob = null; let u1 = genUUID(), u2 = genUUID();
function genUUID() { return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => { const r = Math.random()*16|0; return (c=='x'?r:(r&0x3|0x8)).toString(16); }); }
function toggleMenu() { document.getElementById('sidebar').classList.toggle('active'); }
function setTheme(t) { document.body.className = t + '-theme'; toggleMenu(); }
function processIcon() {
    const file = document.getElementById('icon-input').files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image(); img.onload = () => {
            const canvas = document.getElementById('canvas'); const ctx = canvas.getContext('2d');
            let size = Math.min(img.width, img.height); ctx.clearRect(0,0,128,128);
            ctx.drawImage(img, (img.width-size)/2, (img.height-size)/2, size, size, 0, 0, 128, 128);
            canvas.toBlob(blob => { iconBlob = blob; document.getElementById('icon-preview').src = URL.createObjectURL(blob); document.getElementById('icon-preview').style.display = 'block'; }, 'image/png');
        }; img.src = e.target.result;
    }; reader.readAsDataURL(file);
}
function liveUpdate() {
    const name = document.getElementById("name").value || "Pack";
    const engine = document.getElementById("engine").value.split(",").map(Number);
    currentJSON = { "format_version": 2, "header": { "name": name, "uuid": u1, "version": [1,0,0], "min_engine_version": engine }, "modules": [{"type": "resources", "uuid": u2, "version": [1,0,0]}] };
    document.getElementById("preview").innerText = JSON.stringify(currentJSON, null, 4);
}
async function handleDownload() {
    const res = await fetch("/download", { method: "POST", body: JSON.stringify(currentJSON) });
    const b = await res.blob(); saveAs(b, "manifest.json");
    if(iconBlob) setTimeout(() => saveAs(iconBlob, "pack_icon.png"), 500);
}
function saveAs(blob, name) { const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = name; a.click(); }
function copyJSON() { navigator.clipboard.writeText(JSON.stringify(currentJSON, null, 4)); alert("Copied!"); }
liveUpdate();
</script>
</body>
</html>
'''

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(force=True)
    with open("manifest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return send_file("manifest.json", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
