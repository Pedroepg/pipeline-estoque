import random
from datetime import date, timedelta
import pandas as pd

random.seed(42)

produtos = pd.read_csv("data/produtos.csv")
fornecedores = pd.read_csv("data/fornecedores.csv")

INICIO = date(2026, 1, 1)
FIM = date(2026, 9, 30)
DIAS = (FIM - INICIO).days
N_SAIDAS = 3000

ids = produtos["id_produto"].tolist()

# Cada produto tem um fornecedor fixo
forn_do_produto = {i: random.choice(fornecedores["id_fornecedor"].tolist()) for i in ids}

# Popularidade: poucos produtos vendem muito, a maioria vende pouco.
# É isso que vai criar uma curva ABC realista.
pesos = [random.paretovariate(1.2) for _ in ids]

# ---------- SAÍDAS ----------
vendidos = random.choices(ids, weights=pesos, k=N_SAIDAS)
saidas = []
for n, id_prod in enumerate(vendidos, start=1):
    saidas.append({
        "id_saida": n,
        "id_produto": id_prod,
        "data_saida": INICIO + timedelta(days=random.randint(0, DIAS)),
        "quantidade": random.randint(1, 10),
    })
df_saidas = pd.DataFrame(saidas)

# ---------- RECEBIMENTOS ----------
# Uma entrada por mês por produto, proporcional ao que o produto vende
total_vendido = df_saidas.groupby("id_produto")["quantidade"].sum().to_dict()

recebimentos = []
n = 1
for id_prod in ids:
    por_mes = total_vendido.get(id_prod, 0) / 9
    for mes in range(9):
        qtd_nf = max(10, round(por_mes * random.uniform(0.8, 1.3)))
        if mes == 0:
            qtd_nf += round(por_mes)   # estoque inicial
        qtd_conf = qtd_nf
        if random.random() < 0.12:     # ~12% dos recebimentos com divergência
            qtd_conf = max(0, qtd_nf - random.randint(1, 8))
        recebimentos.append({
            "id_recebimento": n,
            "id_produto": id_prod,
            "id_fornecedor": forn_do_produto[id_prod],
            "data_recebimento": INICIO + timedelta(days=mes * 30 + random.randint(0, 5)),
            "qtd_nota_fiscal": qtd_nf,
            "qtd_conferida": qtd_conf,
        })
        n += 1
df_receb = pd.DataFrame(recebimentos)

df_saidas.to_csv("data/saidas.csv", index=False)
df_receb.to_csv("data/recebimentos.csv", index=False)

print(df_saidas.head())
print(df_receb.head())
print("Divergências:", (df_receb["qtd_nota_fiscal"] != df_receb["qtd_conferida"]).mean().round(3))