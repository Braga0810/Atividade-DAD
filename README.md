# API Moradia — Microsserviço

Microsserviço responsável pela tabela **Moradia** do projeto de censo da
disciplina **Desenvolvimento de Aplicações Distribuídas** (PUC Minas).
Coleta, armazena e disponibiliza os dados de moradia dos estudantes via
API REST (HTTP + JSON) e oferece um front-end web para gerenciá-los.

---

## 1. Como rodar

```bash
# 1) instalar dependências
pip install -r requirements.txt

# 2) (opcional) popular com dados de exemplo
python seed.py

# 3) iniciar o serviço
python api/app.py
```

Depois acesse:

- **Front-end:** http://localhost:5005/
- **API:** http://localhost:5005/moradias

Por padrão usa **SQLite** (cria o arquivo `moradia.db`), sem precisar instalar
banco nenhum.

---

## 2. Banco de dados

Funciona com SQLite (padrão) ou MySQL (banco compartilhado `bd_censo`).
Para usar MySQL, defina variáveis de ambiente antes de rodar:

```bash
export DB_BACKEND=mysql
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=suasenha
export DB_NAME=bd_censo
python app.py
```

Estrutura da tabela (modelo original):

| Campo                | Tipo          | Descrição                          |
|----------------------|---------------|------------------------------------|
| estudante (PK/FK)    | INTEGER       | Matrícula (→ DadosPessoais)        |
| tipo                 | VARCHAR(15)   | Casa, Apartamento, República…      |
| bairro               | VARCHAR(60)   |                                    |
| cidade               | VARCHAR(50)   |                                    |
| distancia_faculdade  | DECIMAL(5,2)  | em km                              |
| mora_quem            | VARCHAR(60)   | Sozinho, Família, Amigos…          |
| propria              | INTEGER       | 1 = própria, 0 = alugada/cedida    |

---

## 3. Endpoints da API

| Método | Rota                              | Descrição                                   |
|--------|-----------------------------------|---------------------------------------------|
| GET    | `/health`                         | Status do serviço                           |
| GET    | `/moradias`                       | Lista todas (filtros: `?cidade=&bairro=&tipo=`) |
| GET    | `/moradias/<matricula>`           | Busca uma moradia                           |
| GET    | `/moradias/<matricula>/completo`  | Moradia + dados do estudante (integração)   |
| GET    | `/moradias/estatisticas`          | Indicadores agregados                       |
| POST   | `/moradias`                       | Cadastra (JSON no corpo)                    |
| PUT    | `/moradias/<matricula>`           | Atualiza                                    |
| DELETE | `/moradias/<matricula>`           | Remove                                      |

### Exemplo de criação

```bash
curl -X POST http://localhost:5005/moradias \
  -H "Content-Type: application/json" \
  -d '{
        "estudante": 1010,
        "tipo": "Apartamento",
        "bairro": "Coração Eucarístico",
        "cidade": "Belo Horizonte",
        "distancia_faculdade": 1.5,
        "mora_quem": "Família",
        "propria": false
      }'
```

---

## 4. Comunicação entre microsserviços

Este serviço consulta a API do grupo de **DadosPessoais** para validar a
matrícula e enriquecer respostas (rota `/completo`). A URL é configurável:

```bash
export DADOS_PESSOAIS_API_URL=http://localhost:5001
```

Se essa API estiver **offline**, o serviço de Moradia continua funcionando
normalmente em modo isolado (a validação cruzada é apenas ignorada).

---

## 5. Estrutura do projeto

```
api_moradia/
├── app.py                     # ponto de entrada (Flask)
├── config.py                  # configuração via variáveis de ambiente
├── database.py                # modelo Moradia + conexão (SQLite/MySQL)
├── services.py                # regras de negócio + CRUD + estatísticas
├── routes.py                  # endpoints REST
├── dados_pessoais_client.py   # cliente da API de DadosPessoais
├── seed.py                    # dados de exemplo
├── requirements.txt
└── static/index.html          # front-end
```
