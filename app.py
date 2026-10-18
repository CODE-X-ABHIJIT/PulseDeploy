import os
from flask import Flask, jsonify

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "local")

@app.get("/")
def home():
    return jsonify(
        app="PulseDeploy",
        version=VERSION,
        status="running"
    )

@app.get("/health")
def health():
    return jsonify(status="healthy")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
