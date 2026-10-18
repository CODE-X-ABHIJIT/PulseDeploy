
import os

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "local")

DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PulseDeploy | Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0b1120;
            color: #e5e7eb;
        }
        header {
            padding: 24px 8%;
            background: #111827;
            border-bottom: 1px solid #263247;
        }
        header h1 { margin: 0; color: #60a5fa; }
        header p { margin-bottom: 0; color: #9ca3af; }
        main { max-width: 1100px; margin: 45px auto; padding: 0 20px; }
        .hero { margin-bottom: 32px; }
        .hero h2 { font-size: 32px; margin-bottom: 8px; }
        .hero p { color: #9ca3af; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }
        .card {
            padding: 25px;
            background: #151f32;
            border: 1px solid #29364d;
            border-radius: 14px;
        }
        .card h3 { color: #9ca3af; font-size: 14px; }
        .value { font-size: 24px; font-weight: bold; margin: 18px 0 8px; }
        .healthy { color: #4ade80; }
        .dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 8px;
        }
        .info {
            margin-top: 24px;
            padding: 24px;
            background: #111827;
            border-radius: 14px;
            line-height: 1.8;
        }
        footer { text-align: center; padding: 30px; color: #6b7280; }
    </style>
</head>
<body>
    <header>
        <h1>PulseDeploy</h1>
        <p>CI/CD Deployment Dashboard</p>
    </header>
    <main>
        <section class="hero">
            <h2>Application Overview</h2>
            <p>Monitor your application's current runtime status.</p>
        </section>

        <section class="grid">
            <div class="card">
                <h3>APPLICATION</h3>
                <div class="value">PulseDeploy</div>
                <span>Flask Web Application</span>
            </div>
            <div class="card">
                <h3>APPLICATION STATUS</h3>
                <div class="value healthy">
                    <span class="dot"></span>Running
                </div>
                <span>Application is responding</span>
            </div>
            <div class="card">
                <h3>HEALTH CHECK</h3>
                <div class="value healthy">Healthy</div>
                <span>Endpoint: /health</span>
            </div>
            <div class="card">
                <h3>APPLICATION VERSION</h3>
                <div class="value">{{ version }}</div>
                <span>Current application build</span>
            </div>
        </section>

        <section class="info">
            <strong>Deployment information</strong><br>
            Delivery pipeline: Jenkins<br>
            Container registry: GitHub Container Registry<br>
            Orchestration: Kubernetes<br>
            Dashboard: Operational
        </section>
    </main>
    <footer>PulseDeploy · Built for CI/CD learning</footer>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(DASHBOARD, version=VERSION)


@app.route("/health")
def health():
    return jsonify(status="healthy")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
