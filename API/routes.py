"""
Endpoints REST do microsserviço de Moradia.

Todos respondem em JSON e seguem o padrão de microsserviços:
- recursos no plural (/moradias)
- verbos HTTP (GET, POST, PUT, DELETE) para as operações
- códigos de status apropriados (200, 201, 400, 404, 409)
"""
from flask import Blueprint, jsonify, request

import services
import dados_pessoais_client as dp

bp = Blueprint("moradias", __name__)


# ----------------------------------------------------------------------------
# Saúde do serviço
# ----------------------------------------------------------------------------
@bp.get("/health")
def health():
    """Verifica se o serviço está no ar (usado por outros grupos e por monitoramento)."""
    return jsonify({
        "servico": "api-moradia",
        "status": "ok",
        "dados_pessoais_api": "online" if dp.api_online() else "offline",
    })


# ----------------------------------------------------------------------------
# CRUD de Moradia
# ----------------------------------------------------------------------------
@bp.get("/moradias")
def listar_moradias():
    """Lista todas as moradias. Aceita filtros: ?cidade=&bairro=&tipo="""
    filtros = {
        "cidade": request.args.get("cidade"),
        "bairro": request.args.get("bairro"),
        "tipo": request.args.get("tipo"),
    }
    dados = services.listar(filtros)
    return jsonify({"total": len(dados), "moradias": dados})


@bp.get("/moradias/estatisticas")
def estatisticas_moradias():
    """Retorna indicadores agregados sobre as moradias cadastradas."""
    return jsonify(services.estatisticas())


@bp.get("/moradias/<int:estudante>")
def obter_moradia(estudante):
    """Retorna a moradia de um estudante específico."""
    moradia = services.buscar(estudante)
    if not moradia:
        return jsonify({"erro": "Moradia não encontrada para esta matrícula."}), 404
    return jsonify(moradia)


@bp.get("/moradias/<int:estudante>/completo")
def obter_moradia_completa(estudante):
    """
    Retorna a moradia + os dados do estudante obtidos na API de DadosPessoais.
    Demonstra a comunicação entre microsserviços. Se a API do outro grupo
    estiver indisponível, devolve a moradia mesmo assim (campo estudante_info=null).
    """
    moradia = services.buscar(estudante)
    if not moradia:
        return jsonify({"erro": "Moradia não encontrada para esta matrícula."}), 404

    info = dp.buscar_estudante(estudante)
    return jsonify({"moradia": moradia, "estudante_info": info})


@bp.post("/moradias")
def criar_moradia():
    """Cadastra uma nova moradia. Corpo JSON deve conter ao menos 'estudante'."""
    payload = request.get_json(silent=True) or {}
    estudante = payload.get("estudante")

    # Validação cruzada (opcional): avisa se a matrícula não existe na outra API,
    # mas não impede o cadastro caso a API esteja offline.
    if estudante is not None and dp.api_online():
        if dp.buscar_estudante(estudante) is None:
            return jsonify({
                "erro": f"Matrícula {estudante} não encontrada na API de DadosPessoais."
            }), 400

    try:
        criada = services.criar(estudante, payload)
    except services.ErroValidacao as e:
        # 409 quando já existe; 400 para os demais erros de validação.
        codigo = 409 if "Já existe" in str(e) else 400
        return jsonify({"erro": str(e)}), codigo

    return jsonify(criada), 201


@bp.get("/estudante/<int:matricula>")
def proxy_estudante(matricula):
    """Proxy para a API de DadosPessoais — permite o front-end validar a matrícula."""
    info = dp.buscar_estudante(matricula)
    if info is None:
        return jsonify({"erro": "Estudante não encontrado ou API indisponível."}), 404
    return jsonify(info)


@bp.put("/moradias/<int:estudante>")
def atualizar_moradia(estudante):
    """Atualiza os dados de uma moradia existente."""
    payload = request.get_json(silent=True) or {}
    try:
        atualizada = services.atualizar(estudante, payload)
    except services.ErroValidacao as e:
        return jsonify({"erro": str(e)}), 400

    if atualizada is None:
        return jsonify({"erro": "Moradia não encontrada para esta matrícula."}), 404
    return jsonify(atualizada)


@bp.delete("/moradias/<int:estudante>")
def remover_moradia(estudante):
    """Remove a moradia de um estudante."""
    if services.remover(estudante):
        return jsonify({"mensagem": f"Moradia do estudante {estudante} removida."})
    return jsonify({"erro": "Moradia não encontrada para esta matrícula."}), 404
