"""
Popula o banco com alguns registros de exemplo para demonstração.

Uso:
    python seed.py
"""
from database import init_db, get_session, Moradia

EXEMPLOS = [
    dict(estudante=1001, tipo="Apartamento", bairro="Coração Eucarístico",
         cidade="Belo Horizonte", distancia_faculdade=1.20, mora_quem="Família", propria=1),
    dict(estudante=1002, tipo="República", bairro="Padre Eustáquio",
         cidade="Belo Horizonte", distancia_faculdade=3.50, mora_quem="Amigos", propria=0),
    dict(estudante=1003, tipo="Casa", bairro="Eldorado",
         cidade="Contagem", distancia_faculdade=8.70, mora_quem="Família", propria=1),
    dict(estudante=1004, tipo="Kitnet", bairro="Carlos Prates",
         cidade="Belo Horizonte", distancia_faculdade=2.10, mora_quem="Sozinho", propria=0),
    dict(estudante=1005, tipo="Apartamento", bairro="Industrial",
         cidade="Contagem", distancia_faculdade=12.40, mora_quem="Cônjuge", propria=0),
]


def main():
    init_db()
    with get_session() as s:
        criados = 0
        for ex in EXEMPLOS:
            if not s.get(Moradia, ex["estudante"]):
                s.add(Moradia(**ex))
                criados += 1
        s.commit()
    print(f"Seed concluído. {criados} registro(s) inserido(s).")


if __name__ == "__main__":
    main()
