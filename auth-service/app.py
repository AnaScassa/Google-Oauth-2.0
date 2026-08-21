from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/verify", methods=["GET"])
def verify():
    authorization = request.headers.get("Authorization")

    if not authorization:
        return jsonify({"authenticated": False}), 401

    return jsonify({
        "authenticated": True,
        "user_id": "123",
        "email": "teste@gmail.com"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)