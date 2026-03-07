import subprocess
import psutil
import time
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

devices = {
    "Starlink": "192.168.110.1",
    "RouterUtama": "192.168.110.2",
    "RouterCCTV": "192.168.110.69",
    "CCTV": "192.168.110.3"
}

def ping(ip):
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", "500", ip],
            stdout=subprocess.DEVNULL
        )
        return result.returncode == 0
    except:
        return False


def check_ai():
    target = "Hybrid YOLO + CNN RTX 4070 Ti STABLE"

    for p in psutil.process_iter(['cmdline']):
        try:
            if target.lower() in str(p.info['cmdline']).lower():
                return True
        except:
            pass

    return False


def gpu():
    try:
        out = subprocess.check_output(
            "nvidia-smi --query-gpu=utilization.gpu,memory.used,temperature.gpu --format=csv,noheader,nounits",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        usage, mem, temp = out.split(",")

        return {
            "usage": usage.strip(),
            "memory": mem.strip(),
            "temp": temp.strip()
        }

    except:
        return {
            "usage": "-",
            "memory": "-",
            "temp": "-"
        }


@app.route("/")
def dashboard():
    return send_from_directory(".", "ai_monitor_dashboard.html")


@app.route("/status")
def status():

    data = {}

    for k, v in devices.items():
        data[k] = ping(v)

    data["AI"] = check_ai()
    data["GPU"] = gpu()
    data["time"] = time.strftime("%H:%M:%S")

    return jsonify(data)


app.run(host="0.0.0.0", port=5000)
