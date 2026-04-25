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
    background: linear-gradient(135deg, #0f172a, #020617);
    color:white;
}

.app {
    max-width:420px;
    margin:auto;
    padding:20px;
}

.header {
    text-align:center;
    margin-bottom:20px;
}

.header h2 {
    margin:0;
}

.header p {
    color:#94a3b8;
    font-size:13px;
}

.card {
    background: rgba(30,41,59,0.8);
    backdrop-filter: blur(10px);
    padding:20px;
    border-radius:20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

input, select {
    width:100%;
    padding:12px;
    margin:8px 0;
    border-radius:10px;
    border:none;
    font-size:16px;
}

button {
    width:100%;
    padding:14px;
    border:none;
    border-radius:14px;
    background: linear-gradient(135deg, #facc15, #f59e0b);
    font-weight:bold;
    margin-top:10px;
    transition:0.2s;
}

button:active {
    transform: scale(0.96);
}

.preview {
    margin-top:15px;
    background:#020617;
    padding:10px;
    border-radius:10px;
    font-size:12px;
    max-height:200px;
    overflow:auto;
}

.loading {
    text-align:center;
    margin-top:10px;
    display:none;
}

.small-btn {
    background:#38bdf8;
}
</style>
</head>

<body>

<div class="app">

<div class="header">
  <h2>🧱 Manifest Generator</h2>
  <p>Minecraft Bedrock Tool</p>
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
<button class="small-btn" onclick="download()">Download</button>
<button class="small-btn" onclick="copyJSON()">Copy JSON</button>

<div id="loading" class="loading">⏳ Generating...</div>

<div class="preview" id="preview">JSON preview...</div>

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
                name: name,
                desc: desc,
                ver: ver,
                engine: engine
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

    alert("Copied JSON!");
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)