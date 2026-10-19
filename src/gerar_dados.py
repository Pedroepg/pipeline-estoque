import random
import pandas as pd
from faker import Faker

random.seed(42)          # garante que os dados saiam iguais toda vez
fake = Faker("pt_BR")
Faker.seed(42)

def gerar_fornecedores(qtd=8):
    linhas = []
    for i in range(1, qtd + 1):
        linhas.append({
            "id_fornecedor": i,
            "nome": fake.company(),
            "prazo_entrega_dias": random.randint(2, 15),
        })
    return pd.DataFrame(linhas)

fornecedores = gerar_fornecedores()
fornecedores.to_csv("data/fornecedores.csv", index=False)
print(fornecedores)