from flask import Flask, render_template, redirect

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/", methods=["GET"])
def index() -> str:
    return render_template("index.html")

@app.route("/profile", methods=["GET"])
def profile() -> str:
    return render_template("profile.html", user_info={"name": "Nome do Usuário", "email": "email@dominio.com"})

@app.route("/login/google", methods=["GET"])
def login_google() -> str:
    return redirect("https://accounts.google.com/o/oauth2/auth")

if __name__ == "__main__":
    app.run(port=8080, debug=True, ssl_context="adhoc")
    #porta que o arquivo vai rodar, debug para atualizar automaticamente e ssl_context para rodar com https