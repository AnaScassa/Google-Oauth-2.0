import os

from flask import Flask, Response, redirect, request, session, url_for
from dataclasses import dataclass
import requests
from oauthlib.oauth2 import WebApplicationClient

server = Flask(__name__)
server.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

#em uma aplicação séria nao pode deixar essas chaves a mostra!
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.environ.get("GOOGLE_SECRET")

client = WebApplicationClient(client_id=GOOGLE_CLIENT_ID)
@dataclass
class GoogleHosts:
    autorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    certs: str

def get_google_oauth_hosts() -> GoogleHosts:
    hosts = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if hosts.status_code != 200:
        raise Exception("Failed to fetch Google OAuth hosts")
    data = hosts.json()
    return GoogleHosts(
        autorization_endpoint=data.get('authorization_endpoint'),
        token_endpoint=data.get('token_endpoint'),
        userinfo_endpoint=data.get('userinfo_endpoint'),
        certs=data.get('jwks_uri')
    )

@server.route('/auth/login', methods=['GET'])
def login() -> Response:
    hosts = get_google_oauth_hosts()

    authorization_url = client.prepare_request_uri(
        hosts.autorization_endpoint,
        redirect_uri=url_for('callback', _external=True),
        scope=["openid", "email", "profile"]
    )

    return redirect(location=authorization_url)

@server.route('/auth/callback', methods=['GET'])
def callback() -> Response:
    hosts = get_google_oauth_hosts()
    code = request.args.get('code')
    if not code:
        return Response('Missing authorization code', status=400)

    token_url, headers, body = client.prepare_token_request(
        hosts.token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for('callback', _external=True),
        code=code,
        client_secret=GOOGLE_SECRET
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_SECRET),
    )
    token_response.raise_for_status()
    client.parse_request_body_response(token_response.text)

    uri, headers, body = client.add_token(hosts.userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_response.raise_for_status()
    user_info = userinfo_response.json()

    session['user_info'] = {
        'name': user_info.get('name'),
        'email': user_info.get('email')
    }

    return redirect(url_for('profile'))

@server.route('/profile', methods=['GET'])
def profile() -> Response:
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    return Response(f"<h1>Bem vindo, {user_info['name']}</h1><p>{user_info['email']}</p>")

if __name__ == "__main__":
    server.run(port=8081, debug=True, ssl_context="adhoc")
    