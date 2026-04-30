from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Python End-to-End DevOps Application Deployed Successfully!"

@app.route("/health")
def health():
    return {"status": "running"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
