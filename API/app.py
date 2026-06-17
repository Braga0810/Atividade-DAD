"""
Ponto de entrada do microsserviço de Moradia.

Para rodar:
    pip install -r requirements.txt
    python app.py

A API ficará disponível em http://localhost:5005
O front-end (página web) em http://localhost:5005/
"""
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config
from database import init_db
from routes import bp


def criar_app() -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    # CORS liberado: permite que o front-end e as APIs de outros grupos
    # (em outras portas/origens) consumam este serviço.
    CORS(app)

    # Cria a tabela no banco, se necessário.
    init_db()

    # Registra os endpoints da API.
    app.register_blueprint(bp)

    # Front-end: serve a página principal na raiz.
    @app.get("/")
    def index():
        return send_from_directory("static", "index.html")

    return app


app = criar_app()


if __name__ == "__main__":
    print("=" * 60)
    print("  Microsserviço de MORADIA — Censo (DAD / PUC Minas)")
    print("=" * 60)
    print(f"  Banco de dados : {Config.DB_BACKEND}")
    print(f"  API DadosPessoais: {Config.DADOS_PESSOAIS_API_URL}")
    print(f"  Front-end      : http://localhost:{Config.PORT}/")
    print(f"  API base       : http://localhost:{Config.PORT}/moradias")
    print("=" * 60)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
