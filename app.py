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
<title>Manifest Generator</title>

<link rel="icon" href="https://www.minecraft.net/etc.clientlibs/minecraft/clientlibs/main/resources/favicon.ico">

<style>
body {
    margin:0;
    font-family:sans-serif;
    background: radial-gradient(circle at top, #1e1b4b, #020617);
    color:white;
    overflow-x:hidden;
}

/* Glow nền */
body::before {
    content:"";
    position:fixed;
    width:300px;
    height:300px;
    background:#7c3aed;
    filter:blur(120px);
    top:-100px;
    left:-100px;
    opacity:0.5;
}

body::after {
    content:"";
    position:fixed;
    width:300px;
    height:300px;
    background:#22d3ee;
    filter:blur(120px);
    bottom:-100px;
    right:-100px;
    opacity:0.5;
}

.app {
    max-width:420px;
    margin:auto;
    padding:20px;
    position:relative;
}

/* Header */
.header {
    text-align:center;
    margin-bottom:20px;
}

.header h2 {
    margin:0;
    background: linear-gradient(90deg,#c084fc,#22d3ee);
    -webkit-background-clip:text;
    color:transparent;
}

.header p {
    color:#a5b4fc;
    font-size:13px;
}

/* Card */
.card {
    background: rgba(30,41,59,0.6);
    backdrop-filter: blur(15px);
    padding:20px;
    border-radius:20px;
    border:1px solid rgba(255,255,255,0.05);
    box-shadow: 0 0 30px rgba(124,58,237,0.3);
}

/* Input */
input, select {
    width:100%;
    padding:12px;
    margin:8px 0;
    border-radius:10px;
    border:none;
    background:#020617;
    color:white;
    outline:none;
}

/* Button neon */
button {
    width:100%;
    padding:14px;
    border:none;
    border-radius:14px;
    background: linear-gradient(135deg,#7c3aed,#22d3ee);
    font-weight:bold;
    margin-top:10px;
    color:white;
    box-shadow: 0 0 15px rgba(124,58,237,0.6);
    transition:0.2s;
}

button:hover {
    box-shadow: 0 0 25px rgba(34,211,238,0.8);
}

button:active {
    transform: scale(0.96);
}

/* Preview */
.preview {
    margin-top:15px;
    background:#020617;
    padding:10px;
    border-radius:10px;
    font-size:12px;
    max-height:200px;
    overflow:auto;
    border:1px solid rgba(255,255,255,0.05);
}

/* Loading */
.loading {
    text-align:center;
    margin-top:10px;
    display:none;
    color:#22d3ee;
}

/* Footer */
.footer {
    text-align:center;
    margin-top:20px;
    font-size:12px;
    color:#64748b;
}
</style>
</head>

<body>

<div class="app">

<div class="header">
  <h2>🧱 Manifest Generator</h2>
  <p>Minecraft Bedrock Tool • Neon Edition</p>
</div>

<div class="card">

<input id="name" placeholder="Pack Name">
<input id="desc" placeholder="Description">

<input id="ver" placeholder="Version (1,0,0)">

<select id="engine">
  <option value="1,20,0">Engine 1.20.0</option>
  <option value="1,21,0">Engine 1.21.0</option>
  <option value="1,21,50">Engine 1.21.50</option>
</select>

<button onclick="generate()">Generate</button>
<button onclick="download()">Download</button>
<button onclick="copyJSON()">Copy JSON</button>

<div id="loading" class="loading">⏳ Generating...</div>

<div class="preview" id="preview">JSON preview...</div>

</div>

<div class="footer">
Made with ⚡ by you
</div>

</div>

<script>
let currentJSON = null;

async function generate(){
    let name = document.getElementById("name").value;
    let desc = document.getElementById("desc").value;
    let ver = document.getElementById("ver").value;
    let engine = document.getElementById("engine").value;

    if(!name || !desc || !ver){
        alert("Nhập đủ thông tin 😑");
        return;
    }

    document.getElementById("loading").style.display = "block";

    try{
        let res = await fetch("/generate", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                name:name,
                desc:desc,
                ver:ver,
                engine:engine
            })
        });

        let data = await res.json();

        if(!res.ok){
            alert("Lỗi: " + JSON.stringify(data));
            return;
        }

        currentJSON = data;
        document.getElementById("preview").innerText =
            JSON.stringify(data, null, 4);

    }catch(e){
        alert("Fetch lỗi: " + e);
    }

    document.getElementById("loading").style.display = "none";
}

async function download(){
    if(!currentJSON){
        alert("Generate trước!");
        return;
    }

    let res = await fetch("/download", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify(currentJSON)
    });

    let blob = await res.blob();
    let url = URL.createObjectURL(blob);

    let a = document.createElement("a");
    a.href = url;
    a.download = "manifest.json";
    a.click();
}

function copyJSON(){
    if(!currentJSON){
        alert("Generate trước!");
        return;
    }

    navigator.clipboard.writeText(
        JSON.stringify(currentJSON, null, 4)
    );

    alert("Copied!");
}
</script>

</body>
</html>
'''

# ===== GENERATE =====
@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)

        name = data.get("name")
        desc = data.get("desc")
        ver = data.get("ver")
        engine = data.get("engine")

        if not name or not desc or not ver or not engine:
            return jsonify({"error": "Missing fields"}), 400

        version = [int(x) for x in ver.split(",")]
        engine_v = [int(x) for x in engine.split(",")]

        manifest = {
            "format_version": 2,
            "header": {
                "name": name,
                "description": desc,
                "uuid": str(uuid.uuid4()),
                "version": version,
                "min_engine_version": engine_v
            },
            "modules": [
                {
                    "type": "resources",
                    "uuid": str(uuid.uuid4()),
                    "version": version
                }
            ]
        }

        return jsonify(manifest)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== DOWNLOAD =====
@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(force=True)

    with open("manifest.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("manifest.json", as_attachment=True)