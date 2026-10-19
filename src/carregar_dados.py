import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

usuario = os.getenv("POSTGRES_USER")
senha = os.getenv("POSTGRES_PASSWORD")
banco = os.getenv("POSTGRES_DB")
host = os.getenv("POSTGRES_HOST", "localhost")
porta = os.getenv("POSTGRES_PORT", "5433")

engine = create_engine(
    f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}")

# ---------- EXTRACT ----------
fornecedores = pd.read_csv("data/fornecedores.csv")
produtos = pd.read_csv("data/produtos.csv")
recebimentos = pd.read_csv("data/recebimentos.csv",
                           parse_dates=["data_recebimento"])
saidas = pd.read_csv("data/saidas.csv", parse_dates=["data_saida"])

# ---------- TRANSFORM ----------
assert produtos["id_produto"].is_unique, "id_produto duplicado"
assert (recebimentos["qtd_conferida"] >= 0).all(), "qtd_conferida negativa"
assert (saidas["quantidade"] > 0).all(), "quantidade de saída inválida"

# ---------- LOAD ----------
with engine.begin() as conn:
    conn.execute(text("TRUNCATE saidas, recebimentos, produtos, fornecedores"))

    fornecedores.to_sql("fornecedores", conn, if_exists="append", index=False)
    produtos.to_sql("produtos", conn, if_exists="append", index=False)
    recebimentos.to_sql("recebimentos", conn, if_exists="append", index=False)
    saidas.to_sql("saidas", conn, if_exists="append", index=False)

# ---------- CONFERÊNCIA ----------
with engine.connect() as conn:
    for tabela in ["fornecedores", "produtos", "recebimentos", "saidas"]:
        total = conn.execute(text(f"SELECT COUNT(*) FROM {tabela}")).scalar()
        print(f"{tabela}: {total} linhas")
