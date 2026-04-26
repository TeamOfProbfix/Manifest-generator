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
    <title>MC Manifest Generator Pro ⚙️</title>
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

        body { 
            margin:0; font-family: 'Segoe UI', sans-serif; 
            background: var(--bg-grad); color: var(--text-main); 
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
            transition: 0.3s;
        }

        .app { width: 100%; max-width: 480px; padding: 20px; position: relative; }

        /* Sidebar & Menu */
        .menu-btn { position: fixed; top: 20px; right: 20px; cursor: pointer; z-index: 100; padding: 10px; background: var(--card-bg); border-radius: 10px; border: 1px solid var(--border); }
        .menu-btn div { width: 25px; height: 3px; background: var(--s-color); margin: 5px 0; border-radius: 2px; }
        .sidebar { position: fixed; top: 0; right: -250px; width: 200px; height: 100%; background: var(--card-bg); backdrop-filter: blur(20px); padding: 60px 20px; transition: 0.4s; z-index: 90; border-left: 1px solid var(--border); }
        .sidebar.active { right: 0; }
        .theme-opt { display: block; width: 100%; padding: 12px; margin-bottom: 10px; border: 1px solid var(--border); background: var(--input-bg); color: var(--text-main); border-radius: 10px; cursor: pointer; text-align: left; }

        .header { text-align: center; margin-bottom: 20px; }
        .header h2 { margin: 0; font-size: 24px; background: linear-gradient(90deg, #c084fc, var(--s-color)); -webkit-background-clip: text; color: transparent; }
        
        .card { background: var(--card-bg); backdrop-filter: blur(15px); padding: 25px; border-radius: 24px; border: 1px solid var(--border); box-shadow: 0 10px 40px rgba(0,0,0,0.4); }

        .input-group { margin-bottom: 15px; }
        label { display: block; font-size: 11px; color: var(--text-sub); margin-bottom: 5px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;}
        input, select { width: 100%; padding: 12px; border-radius: 12px; border: 1px solid var(--border); background: var(--input-bg); color: var(--text-main); font-size: 14px; box-sizing: border-box; transition: 0.2s; }
        input:focus { border-color: var(--s-color); outline: none; box-shadow: 0 0 10px rgba(34, 211, 238, 0.2); }

        .uuid-box { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 10px; font-family: monospace; font-size: 10px; color: var(--s-color); margin-bottom: 10px; border: 1px solid var(--border); position: relative;}
        .uuid-actions { display: flex; gap: 5px; margin-bottom: 15px; }
        .btn-small { flex: 1; padding: 8px; font-size: 11px; border-radius: 8px; border: 1px solid var(--border); background: var(--card-bg); color: white; cursor: pointer; }
        .btn-small:hover { background: var(--s-color); color: black; }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

        .btn-main { width: 100%; padding: 15px; border: none; border-radius: 15px; background: linear-gradient(135deg, var(--p-color), var(--s-color)); font-weight: bold; color: white; cursor: pointer; font-size: 15px; transition: 0.2s; margin-top: 10px;}
        .btn-main:active { transform: scale(0.98); }

        pre { background: #000; padding: 15px; border-radius: 12px; font-size: 12px; color: #38bdf8; overflow: auto; max-height: 150px; border: 1px solid var(--border); margin: 15px 0; }
        
        .skin-hint { font-size: 10px; color: #facc15; margin-top: 5px; display: none; }

        .footer { text-align: center; margin-top: 25px; font-size: 11px; color: var(--text-sub); line-height: 1.8; }
        .footer b { color: var(--s-color); }
        .footer a { color: var(--s-color); font-weight: bold; text-decoration: underline; }
    </style>
</head>
<body class="neon-theme">

<div class="menu-btn" onclick="toggleMenu()"><div></div><div></div><div></div></div>
<div class="sidebar" id="sidebar">
    <h4>Themes</h4>
    <button class="theme-opt" onclick="setTheme('neon')">✨ Neon</button>
    <button class="theme-opt" onclick="setTheme('dark')">🌙 Dark</button>
    <button class="theme-opt" onclick="setTheme('light')">☀️ Light</button>
</div>

<div class="app">
    <div class="header"><h2>MC Manifest Generator ⚙️</h2></div>

    <div class="card">
        <div class="input-group">
            <label>Pack Type</label>
            <select id="type" onchange="checkSkinType()">
                <option value="resources">Resources (Textures/Sounds)</option>
                <option value="data">Behavior (Functions/Entities)</option>
                <option value="script">Script (Gametest API)</option>
                <option value="skin_pack">Skin Pack (Legacy)</option>
            </select>
            <div id="skinHint" class="skin-hint">💡 ProTip: Use our <b>Auto Skin Pack</b> tool below for best results!</div>
        </div>

        <div class="grid">
            <div class="input-group">
                <label>Min Engine</label>
                <select id="engine" onchange="liveUpdate()">
                    <option value="1,17,0">1.17.0</option>
                    <option value="1,18,0">1.18.0</option>
                    <option value="1,19,0">1.19.0</option>
                    <option value="1,20,0">1.20.0</option>
                    <option value="1,21,0">1.21.0</option>
                    <option value="1,26,0">1.26.0</option>
                    <option value="1,26,3" selected>1.26.3</option>
                </select>
            </div>
            <div class="input-group">
                <label>Version</label>
                <input id="ver" value="1,0,0" oninput="liveUpdate()">
            </div>
        </div>

        <div class="input-group">
            <label>Pack Name</label>
            <input id="name" placeholder="My Awesome Pack" oninput="liveUpdate()">
        </div>

        <div class="input-group">
            <label>Description</label>
            <input id="desc" placeholder="Something cool..." oninput="liveUpdate()">
        </div>

        <label>UUID Management</label>
        <div class="uuid-box">
            Header: <span id="uuid1_val">...</span><br>
            Module: <span id="uuid2_val">...</span>
        </div>
        <div class="uuid-actions">
            <button class="btn-small" onclick="randomizeUUIDs()">🔄 Random UUIDs</button>
            <button class="btn-small" onclick="copyUUIDs()">📋 Copy UUIDs</button>
        </div>

        <pre id="preview"></pre>

        <button class="btn-main" onclick="handleDownload()">Download manifest.json</button>
    </div>

    <div class="footer">
        <div>Make by <b>Probfix</b> & <b>AI partner⚡</b></div>
        <div>Need a Skin Pack? <a href="https://skin-pack-generator.onrender.com/" target="_blank">Website Auto Skin pack Here</a></div>
        <div>Java Developer? <a href="#" target="_blank">Make a pack.mcmeta for Java here</a></div>
    </div>
</div>

<script>
let u1 = genUUID(), u2 = genUUID();
let currentJSON = null;

function genUUID() { return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => { const r = Math.random()*16|0; return (c=='x'?r:(r&0x3|0x8)).toString(16); }); }

function toggleMenu() { document.getElementById('sidebar').classList.toggle('active'); }
function setTheme(t) { document.body.className = t + '-theme'; toggleMenu(); }

function checkSkinType() {
    const type = document.getElementById('type').value;
    document.getElementById('skinHint').style.display = (type === 'skin_pack') ? 'block' : 'none';
    liveUpdate();
}

function randomizeUUIDs() {
    u1 = genUUID(); u2 = genUUID();
    liveUpdate();
}

function copyUUIDs() {
    const text = `Header UUID: ${u1}\\nModule UUID: ${u2}`;
    navigator.clipboard.writeText(text);
    alert("UUIDs copied to clipboard!");
}

function liveUpdate() {
    const name = document.getElementById("name").value || "Unnamed Pack";
    const desc = document.getElementById("desc").value || "Created with Probfix Tool";
    const type = document.getElementById("type").value;
    const engine = document.getElementById("engine").value.split(",").map(Number);
    const ver = document.getElementById("ver").value.split(",").map(Number);

    document.getElementById('uuid1_val').innerText = u1;
    document.getElementById('uuid2_val').innerText = u2;

    currentJSON = {
        "format_version": 2,
        "header": {
            "name": name,
            "description": desc,
            "uuid": u1,
            "version": ver,
            "min_engine_version": engine
        },
        "modules": [
            {
                "type": type,
                "uuid": u2,
                "version": ver
            }
        ]
    };
    document.getElementById("preview").innerText = JSON.stringify(currentJSON, null, 4);
    
    // Auto-save to LocalStorage
    localStorage.setItem('probfix_manifest_name', name);
    localStorage.setItem('probfix_manifest_desc', desc);
}

async function handleDownload() {
    const res = await fetch("/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(currentJSON)
    });
    const blob = await res.blob();
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "manifest.json";
    a.click();
}

// Load auto-save on startup
window.onload = () => {
    if(localStorage.getItem('probfix_manifest_name')) {
        document.getElementById('name').value = localStorage.getItem('probfix_manifest_name');
        document.getElementById('desc').value = localStorage.getItem('probfix_manifest_desc');
    }
    liveUpdate();
};
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
