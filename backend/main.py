from flask import Flask, Response, request

server = Flask(__name__)


@server.route("/profile", methods=["GET"])
def profile():
    userinfo = request.headers.get("X-Userinfo")

    if not userinfo:
        return Response("Usuário não autenticado", status=401)

    return Response(f"""
        <h1>Perfil</h1>
        <p>Usuário autenticado pelo APISIX!</p>
        <pre>{userinfo}</pre>
    """)


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8081, debug=True, ssl_context="adhoc")