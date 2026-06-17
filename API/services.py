"""
Regras de negócio do serviço de Moradia.

Concentra a validação dos dados, as operações CRUD e o cálculo de
estatísticas. As rotas (routes.py) apenas chamam estas funções.
"""
from sqlalchemy import func

from database import Moradia, get_session

# Campos que podem ser gravados/atualizados (estudante é tratado à parte).
CAMPOS_EDITAVEIS = ("tipo", "bairro", "cidade", "distancia_faculdade", "mora_quem", "propria")


class ErroValidacao(Exception):
    """Lançada quando os dados recebidos são inválidos."""


def _normalizar(payload: dict) -> dict:
    """Valida e converte os campos recebidos no corpo da requisição."""
    dados = {}

    for campo in CAMPOS_EDITAVEIS:
        if campo not in payload:
            continue
        valor = payload[campo]

        if campo == "distancia_faculdade" and valor not in (None, ""):
            try:
                valor = round(float(valor), 2)
            except (TypeError, ValueError):
                raise ErroValidacao("distancia_faculdade deve ser um número.")
            if valor < 0:
                raise ErroValidacao("distancia_faculdade não pode ser negativa.")

        if campo == "propria" and valor not in (None, ""):
            # Aceita true/false, 0/1, "sim"/"não".
            if isinstance(valor, str):
                valor = 1 if valor.strip().lower() in ("1", "true", "sim", "s", "yes") else 0
            else:
                valor = 1 if valor else 0

        if isinstance(valor, str):
            valor = valor.strip() or None

        dados[campo] = valor

    return dados


def listar(filtros: dict | None = None) -> list[dict]:
    """Lista todas as moradias, com filtros opcionais por cidade, bairro e tipo."""
    filtros = filtros or {}
    with get_session() as s:
        consulta = s.query(Moradia)
        if filtros.get("cidade"):
            consulta = consulta.filter(Moradia.cidade.ilike(f"%{filtros['cidade']}%"))
        if filtros.get("bairro"):
            consulta = consulta.filter(Moradia.bairro.ilike(f"%{filtros['bairro']}%"))
        if filtros.get("tipo"):
            consulta = consulta.filter(Moradia.tipo.ilike(f"%{filtros['tipo']}%"))
        return [m.to_dict() for m in consulta.order_by(Moradia.estudante).all()]


def buscar(estudante: int) -> dict | None:
    """Retorna a moradia de um estudante, ou None se não existir."""
    with get_session() as s:
        m = s.get(Moradia, estudante)
        return m.to_dict() if m else None


def criar(estudante: int, payload: dict) -> dict:
    """Cria uma nova moradia vinculada a uma matrícula."""
    if estudante is None:
        raise ErroValidacao("O campo 'estudante' (matrícula) é obrigatório.")
    try:
        estudante = int(estudante)
    except (TypeError, ValueError):
        raise ErroValidacao("'estudante' deve ser um número inteiro (matrícula).")

    dados = _normalizar(payload)
    with get_session() as s:
        if s.get(Moradia, estudante):
            raise ErroValidacao(f"Já existe moradia cadastrada para o estudante {estudante}.")
        nova = Moradia(estudante=estudante, **dados)
        s.add(nova)
        s.commit()
        return nova.to_dict()


def atualizar(estudante: int, payload: dict) -> dict | None:
    """Atualiza a moradia de um estudante. Retorna None se não existir."""
    dados = _normalizar(payload)
    with get_session() as s:
        m = s.get(Moradia, estudante)
        if not m:
            return None
        for campo, valor in dados.items():
            setattr(m, campo, valor)
        s.commit()
        return m.to_dict()


def remover(estudante: int) -> bool:
    """Remove a moradia de um estudante. Retorna True se removeu."""
    with get_session() as s:
        m = s.get(Moradia, estudante)
        if not m:
            return False
        s.delete(m)
        s.commit()
        return True


def estatisticas() -> dict:
    """
    Calcula indicadores agregados sobre as moradias cadastradas.
    Útil para o painel do front-end e para outros serviços consumirem.
    """
    with get_session() as s:
        total = s.query(func.count(Moradia.estudante)).scalar() or 0
        media_dist = s.query(func.avg(Moradia.distancia_faculdade)).scalar()
        proprias = s.query(func.count(Moradia.estudante)).filter(Moradia.propria == 1).scalar() or 0

        por_cidade = dict(
            s.query(Moradia.cidade, func.count(Moradia.estudante))
            .group_by(Moradia.cidade)
            .all()
        )
        por_tipo = dict(
            s.query(Moradia.tipo, func.count(Moradia.estudante))
            .group_by(Moradia.tipo)
            .all()
        )

    return {
        "total_moradias": total,
        "media_distancia_faculdade": round(float(media_dist), 2) if media_dist is not None else None,
        "moradias_proprias": proprias,
        "moradias_nao_proprias": total - proprias,
        "por_cidade": {(k or "Não informado"): v for k, v in por_cidade.items()},
        "por_tipo": {(k or "Não informado"): v for k, v in por_tipo.items()},
    }
