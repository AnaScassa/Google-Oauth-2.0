from flask import Flask, render_template, redirect

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")

@app.route("/profile", methods=["GET"])
def profile() -> str:
    return render_template("profile.html", user_info={"name": "Nome do Usuário", "email": "email@dominio.com"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True, ssl_context="adhoc")