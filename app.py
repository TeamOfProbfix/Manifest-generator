from flask import Flask, request, jsonify, send_file
import uuid, json

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft Manifest Generator Pro</title>
    <style>
        :root { --p-color: #7c3aed; --s-color: #22d3ee; --bg-dark: #020617; }
        
        body { 
            margin:0; font-family: 'Segoe UI', sans-serif; 
            background: radial-gradient(circle at top, #1e1b4b, var(--bg-dark)); 
            color:white; min-height: 100vh; display: flex; align-items: center; justify-content: center;
        }

        .app { width: 100%; max-width: 500px; padding: 15px; box-sizing: border-box; }

        /* Sửa lỗi Title chạm viền và tách hàng */
        .header { text-align: center; margin-bottom: 20px; }
        .header h2 { 
            margin: 0; font-size: clamp(18px, 5vw, 22px); 
            background: linear-gradient(90deg, #c084fc, var(--s-color)); 
            -webkit-background-clip: text; color: transparent;
            display: flex; align-items: center; justify-content: center; gap: 10px;
            white-space: nowrap; /* Giữ tiêu đề trên 1 dòng */
        }
        
        .card { 
            background: rgba(30, 41, 59, 0.8); backdrop-filter: blur(15px); 
            padding: 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .input-group { margin-bottom: 12px; }
        label { display: block; font-size: 11px; color: #a5b4fc; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
        
        input, select { 
            width: 100%; padding: 10px; border-radius: 10px; 
            border: 1px solid #334155; background: #020617; 
            color: white; font-size: 14px; box-sizing: border-box;
        }

        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }

        /* Nhóm nút bấm */
        .btn-group { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px; }
        button { 
            padding: 12px; border: none; border-radius: 12px; 
            background: linear-gradient(135deg, var(--p-color), var(--s-color)); 
            font-weight: bold; color: white; cursor: pointer; transition: 0.2s; font-size: 13px;
        }
        button.secondary { background: #1e293b; color: #94a3b8; border: 1px solid #334155; }
        button:active { transform: scale(0.96); }

        /* Sửa lỗi Preview chuyên nghiệp */
        .preview-box { margin-top: 15px; }
        .preview-label { font-size: 11px; color: #64748b; margin-bottom: 5px; display: flex; justify-content: space-between; }
        pre { 
            background: #000; padding: 15px; border-radius: 10px; 
            font-size: 12px; color: #38bdf8; overflow: auto; 
            max-height: 200px; border: 1px solid #1e293b;
            margin: 0; line-height: 1.5; tab-size: 4;
        }
        
        .footer { text-align: center; margin-top: 15px; font-size: 11px; color: #475569; }
    </style>
</head>
<body>

<div class="app">
    <div class="header">
        <h2>Minecraft Manifest Generator ⚙️</h2>
    </div>

    <div class="card">
        <div class="input-group">
            <label>Loại Pack (Pack Type)</label>
            <select id="type" onchange="liveUpdate()">
                <option value="resources">Resource Pack (Textures/UI)</option>
                <option value="data">Behavior Pack (Add-ons)</option>
                <option value="skin_pack">Skin Pack</option>
                <option value="script">Script Pack (API/Gametest)</option>
            </select>
        </div>

        <div class="input-group">
            <label>Tên Pack</label>
            <input id="name" placeholder="Ví dụ: My Mod" oninput="liveUpdate()">
        </div>

        <div class="input-group">
            <label>Mô tả</label>
            <input id="desc" placeholder="Nhập mô tả..." oninput="liveUpdate()">
        </div>

        <div class="grid">
            <div class="input-group">
                <label>Phiên bản</label>
                <input id="ver" value="1,0,0" oninput="liveUpdate()">
            </div>
            <div class="input-group">
                <label>Engine</label>
                <select id="engine" onchange="liveUpdate()">
                    <option value="1,20,0">1.20.0</option>
                    <option value="1,21,0" selected>1.21.0</option>
                </select>
            </div>
        </div>

        <div class="preview-box">
            <div class="preview-label">
                <span>Dòng mã Manifest.json:</span>
                <span id="copy-text" style="color:var(--s-color)"></span>
            </div>
            <pre id="preview"></pre>
        </div>

        <div class="btn-group">
            <button onclick="download()">Tải (.json)</button>
            <button class="secondary" onclick="copyJSON()">Sao chép mã</button>
            <button class="secondary" style="grid-column: span 2;" onclick="refreshUUID()">Tạo mới bộ UUID</button>
        </div>
    </div>

    <div class="footer">
        Vá lỗi khẩn cấp bởi <b>Probfix</b> & <b>Partner</b> ⚡
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
    const desc = document.getElementById("desc").value || "No description";
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

    // Hiển thị JSON thụt lề chuẩn 4 dấu cách
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
    document.getElementById("copy-text").innerText = "Đã chép!";
    setTimeout(() => document.getElementById("copy-text").innerText = "", 2000);
}

// Khởi chạy ngay khi load
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
