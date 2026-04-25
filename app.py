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
<title>Minecraft Manifest Generator</title>
<h2></> Minecraft Manifest Generator ⚙️</h2>
<link rel="icon" type="image/png" href="/static/favicon.png">

<style>
body {
    margin:0;
    font-family:sans-serif;
    background: radial-gradient(circle at top, #1e1b4b, #020617);
    color:white;
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
}

/* Header */
.header {
    text-align:center;
    margin-bottom:20px;
}

.header h2 {
    margin:0;
    font-size:20px;
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
}

/* Input fix gọn lại */
.input-group {
    margin-bottom:12px;
}

input, select {
    width:100%;
    padding:10px;
    border-radius:10px;
    border:none;
    background:#020617;
    color:white;
    font-size:14px;
}

/* note nhỏ */
.note {
    font-size:11px;
    color:#64748b;
    margin-top:3px;
}

/* Button */
button {
    width:100%;
    padding:13px;
    border:none;
    border-radius:14px;
    background: linear-gradient(135deg,#7c3aed,#22d3ee);
    font-weight:bold;
    margin-top:10px;
    color:white;
}

button:active {
    transform: scale(0.97);
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
  <h2>&lt;/&gt; Minecraft Manifest Generator ⚙️</h2>
  <p>Minecraft Bedrock Tool • Neon Edition</p>
</div>

<div class="card">

<div class="input-group">
<input id="name" placeholder="Pack Name">
</div>

<div class="input-group">
<input id="desc" placeholder="Description">
</div>

<div class="input-group">
<input id="ver" value="1,0,0">
<div class="note">Change version to avoid errors</div>
</div>

<div class="input-group">
<select id="engine">
  <option value="1,17,0">1.17.0</option>
  <option value="1,18,0">1.18.0</option>
  <option value="1,19,0">1.19.0</option>
  <option value="1,20,0" selected>1.20.0</option>
  <option value="1,21,0">1.21.0</option>
  <option value="1,26,0">1.26.0</option>
</select>
<div class="note">you can change to 1.21.130,...</div>
</div>

<button onclick="generate()">Generate</button>
<button onclick="download()">Download</button>
<button onclick="copyJSON()">Copy JSON</button>

<div class="preview" id="preview">JSON preview...</div>

</div>

<div class="footer">
Make by Probfix ⚡<br>
Supported by ChatGPT ⚡
</div>

</div>

<script>
let currentJSON = null;

async function generate(){
    let name = document.getElementById("name").value;
    let desc = document.getElementById("desc").value;
    let ver = document.getElementById("ver").value;
    let engine = document.getElementById("engine").value;

    if(!name || !desc){
        alert("Nhập đủ thông tin 😑");
        return;
    }

    let res = await fetch("/generate", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({name, desc, ver, engine})
    });

    let data = await res.json();

    if(!res.ok){
        alert(JSON.stringify(data));
        return;
    }

    currentJSON = data;
    document.getElementById("preview").innerText =
        JSON.stringify(data, null, 4);
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

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json(force=True)

    with open("manifest.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("manifest.json", as_attachment=True)