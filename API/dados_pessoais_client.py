"""
Cliente para comunicação com o microsserviço de DadosPessoais (outro grupo).

Este módulo demonstra a integração entre serviços exigida pela atividade:
o serviço de Moradia consulta a API de DadosPessoais para validar a matrícula
do estudante e enriquecer a resposta com o nome dele.

Toda a comunicação é tolerante a falhas: se a API do outro grupo estiver
indisponível, o serviço de Moradia continua funcionando normalmente.
"""
import requests

from config import Config


def buscar_estudante(matricula: int):
    """
    Consulta os dados de um estudante na API de DadosPessoais.

    Tenta alguns formatos de endpoint comuns, já que não sabemos exatamente
    como o outro grupo nomeou as rotas. Retorna um dicionário com os dados do
    estudante, ou None se não encontrar / a API estiver fora do ar.
    """
    base = Config.DADOS_PESSOAIS_API_URL.rstrip("/")
    candidatos = [
        f"{base}/dadospessoais/{matricula}",
        f"{base}/dados_pessoais/{matricula}",
        f"{base}/estudantes/{matricula}",
        f"{base}/alunos/{matricula}",
        f"{base}/{matricula}",
    ]

    for url in candidatos:
        try:
            resp = requests.get(url, timeout=Config.HTTP_TIMEOUT)
            if resp.status_code == 200:
                dados = resp.json()
                # A resposta pode vir como objeto único ou dentro de uma lista.
                if isinstance(dados, list):
                    dados = dados[0] if dados else None
                return dados
        except (requests.RequestException, ValueError):
            # Erro de conexão, timeout ou JSON inválido -> tenta o próximo.
            continue

    return None


def api_online() -> bool:
    """Verifica rapidamente se a API de DadosPessoais está acessível."""
    base = Config.DADOS_PESSOAIS_API_URL.rstrip("/")
    for url in (f"{base}/health", base):
        try:
            resp = requests.get(url, timeout=Config.HTTP_TIMEOUT)
            if resp.status_code < 500:
                return True
        except requests.RequestException:
            continue
    return False
