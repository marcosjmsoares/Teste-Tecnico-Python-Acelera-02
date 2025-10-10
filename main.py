import csv
import pandas as pd
import json
from utils_log import log_decorator
#from timer_decorator import time_measure_decorator
import time
from pathlib import Path

setores = {"Vendas", "TI", "Financeiro", "RH", "Operações"} #setores validos

@log_decorator
def extrair_dados_e_consolidar(pasta: str) -> pd.DataFrame:
    caminho = "funcionarios.csv"
    start_time = time.time()

    df = pd.read_csv(caminho) #lendo csv e adicionando em uma tabela

    return df

df = extrair_dados_e_consolidar("dados")
#print(df)
print("------------------------------------")

#normalizar tipos numéricos
df["salario"] = pd.to_numeric(df["salario"], errors="coerce")              # strings viram NaN 
df["bonus_percentual"] = pd.to_numeric(df["bonus_percentual"], errors="coerce")  # strings viram NaN 

#validar campos
df["campos_valido"] = (
    df["nome"].notna()                                                  # nome presente 
    & df["nome"].astype(str).str.strip().ne("")                         # nome não vazio 
    & ~df["nome"].astype(str).str.contains(r"\d", na=False)             # nome sem números (nega contains) 
    & df["area"].isin(setores)                                          # área válida 
    & df["salario"].notna()                                             # salário presente 
    & (df["salario"] >= 0)                                              # salário ≥ 0 
    & df["bonus_percentual"].notna()                                    # bônus presente 
    & df["bonus_percentual"].between(0, 1, inclusive="both")            # 0 ≤ bônus ≤ 1 
)

#calculo bonus
df["bonus_final"] = 1000 + df["salario"] * df["bonus_percentual"] #criando coluna bonus_final

#KPIS
#agrupamento e transformando em dicionario
media_por_area = (df.groupby("area")["salario"].mean().reset_index(name="media_por_area").to_dict(orient="records"))
#agrupamento e transformando em dicionario
quantidade_funcionario_por_area = (df.groupby("area")["id"].count().reset_index(name="quantidade_funcionarios").to_dict(orient="records"))
#somando e transformando em dicionario
bonus_total_geral = float(df["bonus_final"].sum())
df_bonus_total = (pd.DataFrame({"bonus_total_geral": [bonus_total_geral]}).to_dict(orient="records"))
#buscando campos validos e transformando em dicionario
top3_nomes = (df.loc[df["campos_valido"]].nlargest(3, "bonus_final")["nome"].tolist())
top3_funcionarios_maior_bonus = (pd.DataFrame({"top3_funcionarios_maior_bonus": [top3_nomes]}).to_dict(orient="records"))

#gerar relatorios
if df["campos_valido"].any():     # True se existir pelo menos um válido 
    df.loc[df["campos_valido"]].to_csv("relatorio_individual.csv", index=False)  # salva válidos 

if (~df["campos_valido"]).any():  # existe ao menos um False?
    df.loc[~df["campos_valido"]].to_csv("erros.csv", index=False)

#encapsulando tudo em uma unica variavel
kpis = {
    "media_salario_por_area": media_por_area,
    "quantidade_funcionarios_por_area": quantidade_funcionario_por_area,
    "bonus_total_geral": (df_bonus_total),
    "top3_funcionarios_maior_bonus": top3_funcionarios_maior_bonus,
}

#enviando a variavel kpi para o arquivo json
with open("kpis.json", "w", encoding="utf-8") as f:
    json.dump(kpis, f, ensure_ascii=False, indent=2)


#prints para fins de teste
# print(df)
# print("------------------------------------")
# print(media_por_area)
# print("------------------------------------")
# print(quantidade_funcionario_por_area)
# print("------------------------------------")
# print(df_bonus_total)
# print("------------------------------------")
# print(top3_funcionarios_maior_bonus)
# print("------------------------------------")
# df2 = pd.read_csv("relatorio_individual.csv")
# print(df2)
# print("------------------------------------")
# df3 = pd.read_csv("erros.csv")
# print(df3)
# print("------------------------------------")
# print(kpis)