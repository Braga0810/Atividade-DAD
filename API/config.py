"""
Configuração do microsserviço de Moradia.

Todas as opções podem ser sobrescritas por variáveis de ambiente, o que
facilita rodar o serviço em diferentes máquinas (cada grupo pode apontar
para o banco/serviços que quiser sem alterar o código).
"""
import os


class Config:
    # -------- Servidor --------
    # Porta padrão deste microsserviço. Cada grupo costuma usar uma porta
    # diferente (ex.: DadosPessoais 5001, Moradia 5005, etc.).
    PORT = int(os.getenv("PORT", "5005"))
    HOST = os.getenv("HOST", "0.0.0.0")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    # -------- Banco de dados --------
    # "sqlite"  -> roda sem instalar nada (cria o arquivo moradia.db)
    # "mysql"   -> usa o banco compartilhado bd_censo (MySQL)
    DB_BACKEND = os.getenv("DB_BACKEND", "sqlite").lower()

    # Parâmetros usados quando DB_BACKEND = "mysql"
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "bd_censo")

    # Arquivo usado quando DB_BACKEND = "sqlite"
    SQLITE_PATH = os.getenv("SQLITE_PATH", os.path.join(os.path.dirname(__file__), "moradia.db"))

    # -------- Integração com outros microsserviços --------
    # URL base da API do grupo responsável pela tabela DadosPessoais.
    # É usada para validar/enriquecer a matrícula do estudante.
    DADOS_PESSOAIS_API_URL = os.getenv("DADOS_PESSOAIS_API_URL", "http://localhost:5001")

    # Timeout (segundos) para chamadas a outras APIs.
    HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "4"))

    @classmethod
    def database_url(cls) -> str:
        """Monta a URL de conexão do SQLAlchemy de acordo com o backend escolhido."""
        if cls.DB_BACKEND == "mysql":
            return (
                f"mysql+pymysql://{cls.DB_USER}:{cls.DB_PASSWORD}"
                f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}?charset=utf8mb4"
            )
        return f"sqlite:///{cls.SQLITE_PATH}"
