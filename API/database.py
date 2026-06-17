"""
Camada de acesso ao banco de dados.

Define o modelo (tabela) Moradia usando SQLAlchemy. O mesmo código funciona
tanto em SQLite (para desenvolvimento/apresentação) quanto em MySQL
(banco compartilhado bd_censo), bastando trocar a variável DB_BACKEND.
"""
from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker

from config import Config

Base = declarative_base()


class Moradia(Base):
    """
    Mapeamento da tabela Moradia.

    Observação: no modelo original a tabela não possui chave primária própria,
    apenas o índice sobre 'estudante' (FK -> DadosPessoais.matricula). Como a
    relação é 1:1 (cada estudante possui uma moradia), tratamos 'estudante'
    como identificador único do recurso neste microsserviço.
    """
    __tablename__ = "Moradia"

    estudante = Column(Integer, primary_key=True)            # matrícula (FK)
    tipo = Column(String(15))                                # Casa, Apartamento, República...
    bairro = Column(String(60))
    cidade = Column(String(50))
    distancia_faculdade = Column(Numeric(5, 2))              # em km
    mora_quem = Column(String(60))                           # Sozinho, Família, Amigos...
    propria = Column(Integer)                                # 1 = própria, 0 = alugada/cedida

    def to_dict(self) -> dict:
        """Converte o registro em um dicionário pronto para virar JSON."""
        return {
            "estudante": self.estudante,
            "tipo": self.tipo,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "distancia_faculdade": float(self.distancia_faculdade)
            if self.distancia_faculdade is not None
            else None,
            "mora_quem": self.mora_quem,
            "propria": bool(self.propria) if self.propria is not None else None,
        }


# Engine e fábrica de sessões -------------------------------------------------
_engine = create_engine(
    Config.database_url(),
    echo=False,
    future=True,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=_engine, autoflush=False, future=True)


def init_db() -> None:
    """Cria a tabela caso ela ainda não exista."""
    Base.metadata.create_all(_engine)


def get_session():
    """Retorna uma nova sessão de banco."""
    return SessionLocal()
