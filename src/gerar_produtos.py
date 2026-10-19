import random
import pandas as pd
from faker import Faker

random.seed(42)
fake = Faker("pt-BR")
Faker.seed(42)

PECAS = {
    "Pastilha de freio": "Freios",
    "Disco de freio": "Freios",
    "Filtro de óleo": "Filtros",
    "Filtro de ar": "Filtros",
    "Vela de ignição": "Motor",
    "Correia dentada": "Motor",
    "Amortecedor": "Suspensão",
    "Bateria 60Ah": "Elétrica"
}
MARCAS = ["Bosch", "Cobreq", "Mahle", "Nakata"]

def gerar_produtos(qtd=30):
    combinacoes = []
    for peca in PECAS:
        for marca in MARCAS:
            combinacoes.append((peca, marca))

    escolhidas = random.sample(combinacoes, qtd)

    linhas = []
    for i, (peca, marca) in enumerate(escolhidas, start=1):
        linhas.append({
            "id_produto": i,
            "descricao": f"{peca} {marca}",
            "categoria": PECAS[peca],
            "custo_unitario": round(random.uniform(10, 500), 2),
            "estoque_minimo": random.randint(5, 50),
        })
    return pd.DataFrame(linhas)

produtos = gerar_produtos()
produtos.to_csv("data/produtos.csv", index=False)
print(produtos)