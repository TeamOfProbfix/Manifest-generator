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
    <style>
        :root { --p-color: #7c3aed; --s-color: #22d3ee; --bg-dark: #020617; }
        
        body { 
            margin:0; font-family: 'Segoe UI', sans-serif; 
            background: radial-gradient(circle at top, #1e1b4b, var(--bg-dark)); 
            color:white; min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }

        .app { width: 100%; max-width: 500px; padding: 15px; box-sizing: border-box; }

        /* Tiêu đề & Biểu tượng */
        .header { text-align: center; margin-bottom: 25px; }
        .header h2 { 
            margin: 0; font-size: clamp(20px, 6vw, 26px); 
            background: linear-gradient(90deg, #c084fc, var(--s-color)); 
            -webkit-background-clip: text; color: transparent;
            display: flex; align-items: center; justify-content: center; gap: 8px;
            white-space: nowrap; 
        }
        .code-icon {
            font-size: 16px; color: var(--s-color); font-weight: bold; margin-top: 5px;
            letter-spacing: 2px; font-family: monospace;
        }
        
        .card { 
            background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(15px); 
            padding: 22px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .input-group { margin-bottom: 14px; }
        label { display: block; font-size: 11px; color: #a5b4fc; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold; }
        
        input, select { 
            width: 100%; padding: 12px; border-radius: 10px; 
            border: 1px solid #334155; background: #020617; 
            color: white; font-size: 14px; box-sizing: border-box; transition: 0.3s;
        }
        input:focus, select:focus { outline: none; border-color: var(--s-color); box-shadow: 0 0 8px rgba(34, 211, 238, 0.2); }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        /* Đồng bộ hai nút bấm chính */
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 15px; }
        button { 
            padding: 14px; border: none; border-radius: 12px; 
            background: linear-gradient(135deg, var(--p-color), var(--s-color)); 
            font-weight: bold; color: white; cursor: pointer; transition: 0.2s; font-size: 14px;
        }
        button.full-width { grid-column: span 2; background: #1e293b; color: #cbd5e1; border: 1px solid #334155; }
        button:hover { filter: brightness(1.1); }
        button:active { transform: scale(0.96); }

        /* Khung Preview (Đã sửa lỗi text rớt dòng) */
        .preview-box { margin-top: 18px; }
        .preview-label { font-size: 11px; color: #94a3b8; margin-bottom: 6px; display: flex; justify-content: space-between; font-weight: bold;}
        pre { 
            background: #000; padding: 15px; border-radius: 10px; 
            font-size: 12px; color: #38bdf8; overflow-x: auto; overflow-y: auto;
            max-height: 250px; border: 1px solid #1e293b;
            margin: 0; line-height: 1.5; tab-size: 4; white-space: pre; 
        }
        /* Scrollbar cho đẹp */
        pre::-webkit-scrollbar { height: 6px; width: 6px; }
        pre::-webkit-scrollbar-thumb { background: #334155; border-radius: 3px; }
        
        .footer { text-align: center; margin-top: 20px; font-size: 11px; color: #475569; }
        .footer b { color: var(--s-color); }
    </style>
</head>
<body>

<div class="app">
    <div class="header">
        <h2>MC Manifest Generator ⚙️</h2>
        <div class="code-icon">&lt; / &gt;</div>
    </div>

    <div class="card">
        <div class="input-group">
            <label>Pack Type</label>
            <select id="type" onchange="liveUpdate()">
                <option value="resources">Resources</option>
                <option value="data">Behavior</option>
                <option value="skin_pack">Skin Pack</option>
                <option value="script">Script</option>
            </select>
        </div>

        <div class="input-group">
            <label>Pack Name</label>
            <input id="name" placeholder="Example: Ultra Pack" oninput="liveUpdate()">
        </div>

        <div class="input-group">
            <label>Description</label>
            <input id="desc" placeholder="Enter description..." oninput="liveUpdate()">
        </div>

        <div class="grid">
            <div class="input-group">
                <label>Version</label>
                <input id="ver" value="1,0,0" oninput="liveUpdate()">
            </div>
            <div class="input-group">
                <label>Engine Version</label>
                <select id="engine" onchange="liveUpdate()">
                    <option value="1,17,0">1.17.0</option>
                    <option value="1,20,0">1.20.0</option>
                    <option value="1,21,0" selected>1.21.0</option>
                </select>
            </div>
        </div>

        <div class="preview-box">
            <div class="preview-label">
                <span>JSON PREVIEW:</span>
                <span id="copy-text" style="color:var(--s-color)"></span>
            </div>
            <pre id="preview"></pre>
        </div>

        <div class="btn-group">
            <button onclick="download()">Download (.json)</button>
            <button onclick="copyJSON()">Copy Code</button>
            <button class="full-width" onclick="refreshUUID()">Refresh UUIDs</button>
        </div>
    </div>

    <div class="footer">
        Made by <b>Probfix</b> & <b>AI Partner</b> ⚡<br>
        For Minecraft Bedrock Edition
    </div>
</div>

<script>
function genUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

let u1 = genUUID(), u2 = genUUID(), currentJSON = null;

function refreshUUID() {
    u1 = genUUID(); u2 = genUUID();
    liveUpdate();
}

function liveUpdate() {
    const type = document.getElementById("type").value;
    const name = document.getElementById("name").value || "Unnamed Pack";
    const desc = document.getElementById("desc").value || "No description provided.";
    const ver = document.getElementById("ver").value.split(",").map(n => parseInt(n.trim()) || 0);
    const engine = document.getElementById("engine").value.split(",").map(Number);

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
                "type": type === "script" ? "javascript" : type,
                "uuid": u2,
                "version": ver
            }
        ]
    };

    if (type === "script") {
        currentJSON.dependencies = [{ "module_name": "@minecraft/server", "version": "1.1.0" }];
    }

    document.getElementById("preview").innerText = JSON.stringify(currentJSON, null, 4);
}

async function download() {
    if(!currentJSON) return;
    const res = await fetch("/download", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(currentJSON)
    });
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "manifest.json";
    a.click();
}

function copyJSON() {
    navigator.clipboard.writeText(JSON.stringify(currentJSON, null, 4));
    document.getElementById("copy-text").innerText = "Copied! ✓";
    setTimeout(() => document.getElementById("copy-text").innerText = "", 2000);
}

// Chạy lần đầu khi trang load
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
