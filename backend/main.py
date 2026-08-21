from flask import Flask, Response, request, jsonify
import json
import base64

from models import db, User

server = Flask(__name__)

server.config["SQLALCHEMY_DATABASE_URI"] = ("postgresql://postgres:postgres@postgres:5432/googleoauth")
server.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(server)

with server.app_context():
    db.create_all()

@server.route("/profile", methods=["GET"])
def profile():

    userinfo = request.headers.get("X-Userinfo")

    if not userinfo:
        return Response("Usuário não autenticado", status=401)

    try:
        decoded = base64.b64decode(userinfo).decode("utf-8")

        user_data = json.loads(decoded)

    except Exception as e:
        print("Erro ao processar X-Userinfo:", e)
        return Response("Dados do usuário inválidos", status=400)

    print("Usuário recebido:", user_data)

    google_id = user_data.get("sub")
    email = user_data.get("email")
    name = user_data.get("name")
    picture = user_data.get("picture")

    if not google_id:
        return Response("ID do usuário não encontrado", status=400)

    user = User.query.filter_by(google_id=google_id).first()

    if not user:

        user = User(google_id=google_id, email=email, name=name, picture=picture)

        db.session.add(user)
        db.session.commit()

        mensagem = "Usuário cadastrado com sucesso!"

    else:

        mensagem = "Usuário já estava cadastrado."

    return jsonify({
        "user-info": userinfo,
        "message": mensagem,
        "user": {
            "id": user.id,
            "google_id": user.google_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        }
    })

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8081, debug=True, ssl_context="adhoc")