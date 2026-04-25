from flask import Flask, request, send_file, jsonify
import json, uuid

app = Flask(__name__)

@app.route("/")
def home():
    return '''
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Manifest Generator</title>

<style>
body { background:#0f172a; color:white; font-family:sans-serif; margin:0; }
.app { max-width:420px; margin:auto; padding:20px; }
.card { background:#1e293b; padding:20px; border-radius:20px; }
input { width:100%; padding:12px; margin:8px 0; border-radius:10px; border:none; }
button { width:100%; padding:14px; border:none; border-radius:12px; background:#facc15; margin-top:10px; }
.preview { margin-top:15px; background:#020617; padding:10px; border-radius:10px; font-size:12px; max-height:200px; overflow:auto; }
</style>
</head>

<body>
<div class="app">
<h2>🔥 Manifest Generator</h2>

<div class="card">
<input id="name" placeholder="Pack Name">
<input id="desc" placeholder="Description">
<input id="ver" placeholder="Version (1,0,0)">
<input id="engine" placeholder="Min Engine (1,20,0)">

<button onclick="generate()">Generate</button>
<button onclick="download()">Download</button>

<div class="preview" id="preview">JSON preview...</div>
</div>
</div>

<script>
let currentJSON = null;
const BASE = window.location.origin; // FIX quan trọng

async function generate(){
    try{
        let res = await fetch(BASE + "/generate", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                name: name.value,
                desc: desc.value,
                ver: ver.value,
                engine: engine.value
            })
        });

        let data = await res.json();

        if(!res.ok){
            alert("Server lỗi: " + JSON.stringify(data));
            return;
        }

        currentJSON = data;
        preview.innerText = JSON.stringify(data, null, 4);

    }catch(e){
        alert("Fetch lỗi: " + e);
    }
}

async function download(){
    if(!currentJSON){
        alert("Generate trước!");
        return;
    }

    try{
        let res = await fetch(BASE + "/download", {
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

    }catch(e){
        alert("Download lỗi: " + e);
    }
}
</script>

</body>
</html>
'''

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        version = [int(x) for x in data["ver"].split(",")]
        engine = [int(x) for x in data["engine"].split(",")]

        manifest = {
            "format_version": 2,
            "header": {
                "name": data["name"],
                "description": data["desc"],
                "uuid": str(uuid.uuid4()),
                "version": version,
                "min_engine_version": engine
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
    data = request.json

    with open("manifest.json", "w") as f:
        json.dump(data, f, indent=4)

    return send_file("manifest.json", as_attachment=True)

app.run(host="0.0.0.0", port=5000, debug=True)