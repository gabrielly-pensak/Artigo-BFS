import random
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from bfs import carregar_grafo, contar_arestas, recomendar_conexoes

# Configurações do experimento 
PASTA = Path(__file__).parent
ARQUIVO_DADOS = PASTA / "dados" / "facebook_combined.txt.gz"
PASTA_RESULTADOS = PASTA / "resultados"
FRACAO_REMOVIDA = 0.10   
TOP_K = 10               
REPETICOES = 5         
SEMENTE_BASE = 42


def separar_treino_teste(grafo, fracao, rng):
    # Lista cada aresta uma única vez (u < v) e ordena para ser reproduzível
    arestas = sorted((u, v) for u, amigos in grafo.items() for v in amigos if u < v)
    removidas = rng.sample(arestas, int(len(arestas) * fracao))

    # Copia o grafo e retira as arestas sorteadas
    treino = {u: set(amigos) for u, amigos in grafo.items()}
    teste = {}  
    for u, v in removidas:
        treino[u].discard(v)
        treino[v].discard(u)
        teste.setdefault(u, set()).add(v)
        teste.setdefault(v, set()).add(u)

    return treino, teste


def recomendar_aleatorio(treino, usuario, todos, k, rng):
    escolhidos = set()
    while len(escolhidos) < k:
        candidato = rng.choice(todos)
        if candidato != usuario and candidato not in treino[usuario]:
            escolhidos.add(candidato)
    return escolhidos


def avaliar(recomendados, reais, k):

    acertos = len(recomendados & reais)
    return {
        "precisao": acertos / k,
        "revocacao": acertos / len(reais),
        "acertou": 1 if acertos > 0 else 0,
    }


def rodar_uma_vez(grafo, semente):
    """Executa o experimento completo com uma semente."""
    rng = random.Random(semente)
    treino, teste = separar_treino_teste(grafo, FRACAO_REMOVIDA, rng)
    todos = sorted(grafo)

    metricas = {"BFS (amigos em comum)": [], "Aleatório": []}
    for usuario, reais in teste.items():
        if not treino[usuario]:
            continue  # ficou sem amigos no treino: o BFS não tem por onde começar

        # a) Recomendação pelo BFS
        top = recomendar_conexoes(treino, usuario, top_k=TOP_K)
        recomendados_bfs = {candidato for candidato, _, _ in top}
        metricas["BFS (amigos em comum)"].append(avaliar(recomendados_bfs, reais, TOP_K))

        # b) Recomendação aleatória
        recomendados_alea = recomendar_aleatorio(treino, usuario, todos, TOP_K, rng)
        metricas["Aleatório"].append(avaliar(recomendados_alea, reais, TOP_K))

    # Média das métricas de todos os usuários avaliados
    linhas = []
    for metodo, valores in metricas.items():
        df = pd.DataFrame(valores)
        linhas.append({
            "semente": semente,
            "metodo": metodo,
            "usuarios_avaliados": len(df),
            "precisao": df["precisao"].mean(),
            "revocacao": df["revocacao"].mean(),
            "taxa_acerto": df["acertou"].mean(),
        })
    return linhas


def main():
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    grafo = carregar_grafo(ARQUIVO_DADOS)
    print(f"Grafo carregado: {len(grafo)} usuários, {contar_arestas(grafo)} amizades.")
    print(f"Removendo {FRACAO_REMOVIDA:.0%} das amizades, top {TOP_K}, "
          f"{REPETICOES} repetições...\n")

    todas = []
    for i in range(REPETICOES):
        semente = SEMENTE_BASE + i
        todas.extend(rodar_uma_vez(grafo, semente))
        print(f"  Repetição {i + 1}/{REPETICOES} concluída (semente {semente})")

    detalhado = pd.DataFrame(todas)
    detalhado.to_csv(PASTA_RESULTADOS / "exp2_por_repeticao.csv", index=False)

    # Média e desvio-padrão entre as repetições (vai para o artigo)
    metricas = ["precisao", "revocacao", "taxa_acerto"]
    resumo = detalhado.groupby("metodo")[metricas].agg(["mean", "std"])
    resumo_pct = (resumo * 100).round(2)  # em porcentagem
    resumo_pct.to_csv(PASTA_RESULTADOS / "exp2_resumo.csv")

    print(f"\nResultados (%, média ± desvio-padrão de {REPETICOES} repetições):")
    for metodo in resumo.index:
        print(f"\n  {metodo}")
        for m, nome in zip(metricas, [f"Precisão@{TOP_K}", f"Revocação@{TOP_K}",
                                      "Taxa de acerto"]):
            media, dp = resumo.loc[metodo, (m, "mean")], resumo.loc[metodo, (m, "std")]
            print(f"    {nome:<15} {media:7.2%} ± {dp:.2%}")

    # Quantas vezes o BFS é melhor que o aleatório
    p_bfs = resumo.loc["BFS (amigos em comum)", ("precisao", "mean")]
    p_alea = resumo.loc["Aleatório", ("precisao", "mean")]
    if p_alea > 0:
        print(f"\n  O BFS teve precisão {p_bfs / p_alea:.0f}x maior que o aleatório.")
    else:
        print("\n  O aleatório não acertou nenhuma recomendação.")

    # Gráfico de barras agrupadas: métricas x método
    fig, ax = plt.subplots(figsize=(8, 4.5))
    nomes = [f"Precisão@{TOP_K}", f"Revocação@{TOP_K}", "Taxa de acerto"]
    largura = 0.38
    posicoes = range(len(metricas))
    for j, (metodo, cor) in enumerate([("BFS (amigos em comum)", "#4C72B0"),
                                       ("Aleatório", "#C44E52")]):
        valores = [resumo.loc[metodo, (m, "mean")] * 100 for m in metricas]
        barras = ax.bar([p + (j - 0.5) * largura for p in posicoes], valores,
                        largura, label=metodo, color=cor)
        ax.bar_label(barras, fmt="%.1f%%", fontsize=9)
    ax.set_xticks(list(posicoes), nomes)
    ax.set_ylabel("Porcentagem (%)")
    ax.set_title("BFS com amigos em comum vs. recomendação aleatória")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(PASTA_RESULTADOS / "exp2_grafico_validacao.png", dpi=200)

    print(f"\nArquivos salvos em: {PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()
