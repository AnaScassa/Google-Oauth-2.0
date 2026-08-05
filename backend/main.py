import os

from flask import Flask, Response, redirect, request, session, url_for
from dataclasses import dataclass
import requests
from oauthlib.oauth2 import WebApplicationClient

# Cria a aplicação Flask.
server = Flask(__name__)

# A sessão do Flask usa cookies assinados, então precisamos de uma chave secreta.
# Em produção, configure isso como variável de ambiente segura.
server.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

# As credenciais do Google OAuth devem vir do ambiente.
# Assim você evita deixar client_id/client_secret no código fonte.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_SECRET = os.environ.get("GOOGLE_SECRET")

# O cliente WebApplicationClient encapsula o fluxo OAuth2.
client = WebApplicationClient(client_id=GOOGLE_CLIENT_ID)

# Estrutura simples para armazenar os endpoints do Google.
@dataclass
class GoogleHosts:
    autorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    certs: str


def get_google_oauth_hosts() -> GoogleHosts:
    """Busca dinamicamente os endpoints do Google via OpenID Connect."""
    hosts = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if hosts.status_code != 200:
        raise Exception("Failed to fetch Google OAuth hosts")

    data = hosts.json()

    # Esses valores vêm do Google e dizem onde enviar cada requisição.
    return GoogleHosts(
        autorization_endpoint=data.get('authorization_endpoint'),
        token_endpoint=data.get('token_endpoint'),
        userinfo_endpoint=data.get('userinfo_endpoint'),
        certs=data.get('jwks_uri')
    )


@server.route('/auth/login', methods=['GET'])
def login() -> Response:
    """Inicia o fluxo OAuth redirecionando para a tela de login do Google."""
    hosts = get_google_oauth_hosts()

    # Monta a URL de autorização usando o endpoint do Google.
    # O usuário será enviado ao Google para conceder permissão.
    authorization_url = client.prepare_request_uri(
        hosts.autorization_endpoint,
        redirect_uri=url_for('callback', _external=True),
        scope=["openid", "email", "profile"]
    )

    # Retorna um redirect para o Google.
    return redirect(location=authorization_url)


@server.route('/auth/callback', methods=['GET'])
def callback() -> Response:
    """Recebe o código do Google e troca por token + dados do usuário."""
    hosts = get_google_oauth_hosts()
    code = request.args.get('code')
    if not code:
        return Response('Missing authorization code', status=400)

    # Prepara a requisição de troca de código por token.
    token_url, headers, body = client.prepare_token_request(
        hosts.token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for('callback', _external=True),
        code=code,
        client_secret=GOOGLE_SECRET
    )

    # Envia o POST para o endpoint de token do Google.
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_SECRET),
    )
    token_response.raise_for_status()

    # Lê o token de acesso enviado pelo Google.
    client.parse_request_body_response(token_response.text)

    # Usa o token de acesso para buscar dados do usuário.
    uri, headers, body = client.add_token(hosts.userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    userinfo_response.raise_for_status()
    user_info = userinfo_response.json()

    # Guardamos o nome e o email na sessão do Flask.
    session['user_info'] = {
        'name': user_info.get('name'),
        'email': user_info.get('email')
    }

    # Redireciona para a página de perfil local.
    return redirect(url_for('profile'))


@server.route('/profile', methods=['GET'])
def profile() -> Response:
    """Mostra o perfil do usuário se já estiver autenticado."""
    user_info = session.get('user_info')
    if not user_info:
        return redirect(url_for('login'))

    return Response(f"<h1>Bem vindo, {user_info['name']}</h1><p>{user_info['email']}</p>")


if __name__ == "__main__":
    # Roda o servidor Flask em HTTPS local.
    server.run(port=8081, debug=True, ssl_context="adhoc")
    