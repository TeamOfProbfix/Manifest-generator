from flask import Flask, request, jsonify, send_file
import uuid, json
import os

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft Ultimate Manifest Gen</title>
    <style>
        :root { --p-color: #7c3aed; --s-color: #22d3ee; --bg-dark: #020617; }
        body { margin:0; font-family: 'Segoe UI', sans-serif; background: radial-gradient(circle at top, #1e1b4b, var(--bg-dark)); color:white; min-height: 100vh; overflow-x: hidden; }
        body::before { content:""; position:fixed; width:300px; height:300px; background:var(--p-color); filter:blur(120px); top:-100px; left:-100px; opacity:0.3; z-index:-1; }
        body::after { content:""; position:fixed; width:300px; height:300px; background:var(--s-color); filter:blur(120px); bottom:-100px; right:-100px; opacity:0.3; z-index:-1; }

        .app { max-width:600px; margin:auto; padding:20px; }
        .header { text-align:center; margin-bottom:25px; }
        .header h2 { margin:0; font-size:26px; background: linear-gradient(90deg,#c084fc,var(--s-color)); -webkit-background-clip:text; color:transparent; text-transform: uppercase; letter-spacing: 1px; }
        
        .card { background: rgba(30,41,59,0.7); backdrop-filter: blur(20px); padding:25px; border-radius:24px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 50px rgba(0,0,0,0.6); }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .input-group { margin-bottom:15px; }
        label { display: block; font-size: 12px; color: #a5b4fc; margin-bottom: 6px; font-weight: 600; }
        
        input, select { width:100%; padding:12px; border-radius:12px; border:1px solid #334155; background:#0f172a; color:white; font-size:14px; box-sizing: border-box; transition: 0.3s; }
        input:focus { outline: none; border-color: var(--s-color); box-shadow: 0 0 10px rgba(34, 211, 238, 0.2); }

        .btn-group { display: grid; grid-template-columns: 1.5fr 1fr; gap: 10px; margin-top: 20px; }
        button { padding:14px; border:none; border-radius:14px; background: linear-gradient(135deg,var(--p-color),var(--s-color)); font-weight:bold; color:white; cursor:pointer; transition: 0.3s; font-size: 14px; }
        button.secondary { background: #334155; }
        button:hover { filter: brightness(1.1); transform: translateY(-2px); }
        
        /* Sửa lỗi Preview bị dính chữ */
        .preview-container { margin-top: 25px; }
        .preview-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .preview { 
            background:#020617; padding:20px; border-radius:16px; 
            font-size:13px; font-family: 'Consolas', 'Monaco', monospace; 
            max-height:350px; overflow:auto; border: 1px solid #1e293b; 
            color: #38bdf8; white-space: pre-wrap; line-height: 1.5;
            tab-size: 4; /* Đảm bảo dấu cách hiển thị chuẩn */
        }
        
        .footer { text-align:center; margin-top:40px; font-size:12px; color:#64748b; }
        b { color: var(--s-color); }
    </style>
</head>
<body>

<div class="app">
    <div class="header">
        <h2>Minecraft Manifest Pro ⚙️</h2>
        <p style="color:#a5b4fc; font-size:13px;">Resource • Behavior • Skin • Script</p>
    </div>

    <div class="card">
        <div class="input-group">
            <label>Loại Pack (Pack Type)</label>
            <select id="type" onchange="liveUpdate()">
                <option value="resources">Resource Pack (Texture, UI...)</option>
                <option value="data">Behavior Pack (Add-on logic)</option>
                <option value="skin_pack">Skin Pack</option>
                <option value="script">Script Pack (Gametests/JavaScript)</option>
            </select>
        </div>

        <div class="input-group">
            <label>Tên Pack</label>
            <input id="name" placeholder="Ví dụ: Ultra Survival" oninput="liveUpdate()">
        </div>

        <div class="input-group">
            <label>Mô tả</label>
            <input id="desc" placeholder="Mô tả công dụng của pack..." oninput="liveUpdate()">
        </div>

        <div class="grid">
            <div class="input-group">
                <label>Phiên bản Pack</label>
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

        <div class="preview-container">
            <div class="preview-header">
                <span style="font-size: 13px; color: #94a3b8;">JSON Preview:</span>
                <span id="copy-status" style="font-size: 11px; color: #22d3ee;"></span>
            </div>
            <pre class="preview" id="preview"></pre>
        </div>

        <div class="btn-group">
            <button onclick="download()">Tải về manifest.json</button>
            <button class="secondary" onclick="copyJSON()">Copy Code</button>
        </div>
    </div>

    <div class="footer">
        Thực hiện bởi <b>Probfix</b> & <b>AI Partner</b> ⚡<br>
        Dành cho Minecraft Bedrock Edition
    </div>
</div>

<script>
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

let headerUUID = generateUUID();
let moduleUUID = generateUUID();
let currentJSON = null;

function liveUpdate() {
    const type = document.getElementById("type").value;
    const name = document.getElementById("name").value || "Tên Pack";
    const desc = document.getElementById("desc").value || "Mô tả pack của bạn";
    const ver = document.getElementById("ver").value.split(",").map(v => parseInt(v.trim()) || 0);
    const engine = document.getElementById("engine").value.split(",").map(Number);

    currentJSON = {
        "format_version": 2,
        "header": {
            "name": name,
            "description": desc,
            "uuid": headerUUID,
            "version": ver,
            "min_engine_version": engine
        },
        "modules": [
            {
                "type": type === "script" ? "javascript" : type,
                "uuid": moduleUUID,
                "version": ver
            }
        ]
    };

    // Thêm dependencies nếu là Script để script chạy được
    if (type === "script") {
        currentJSON.dependencies = [
            { "module_name": "@minecraft/server", "version": "1.1.0" }
        ];
    }

    // HIỂN THỊ CÓ DẤU CÁCH (4 spaces) ĐỂ NHÌN CHUYÊN NGHIỆP
    document.getElementById("preview").innerText = JSON.stringify(currentJSON, null, 4);
}

async function download() {
    if(!document.getElementById("name").value) { alert("Thiếu tên Pack kìa bạn ơi!"); return; }
    
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
    const status = document.getElementById("copy-status");
    status.innerText = "Copied! ✓";
    setTimeout(() => status.innerText = "", 2000);
}

// Khởi tạo
liveUpdate();
</script>
</body>
</html>
'''

@app.route("/download", methods=["POST"])
def download():
    try:
        data = request.get_json(force=True)
        file_path = "manifest.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
