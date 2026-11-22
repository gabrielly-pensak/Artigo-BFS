
import random
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # gera imagens sem precisar abrir janela
import matplotlib.pyplot as plt
import pandas as pd

from bfs import carregar_grafo, contar_arestas, bfs_niveis, contar_por_nivel

# Configurações do experimento 
PASTA = Path(__file__).parent
ARQUIVO_DADOS = PASTA / "dados" / "facebook_combined.txt.gz"
PASTA_RESULTADOS = PASTA / "resultados"
SEMENTE = 42      
AMOSTRA = 100     
N_MAX = 3         


def validar_com_networkx(grafo, origens):
    try:
        import networkx as nx
    except ImportError:
        print("NetworkX não instalado: validação pulada.")
        return

    G = nx.Graph()
    for u, amigos in grafo.items():
        for v in amigos:
            G.add_edge(u, v)

    for origem in origens:
        nosso = bfs_niveis(grafo, origem, N_MAX)
        referencia = nx.single_source_shortest_path_length(G, origem, cutoff=N_MAX)
        assert nosso == dict(referencia), f"Diferença encontrada no usuário {origem}"
    print(f"Validação OK: nosso BFS = NetworkX em {len(origens)} usuários.")


def main():
    PASTA_RESULTADOS.mkdir(exist_ok=True)

    # 1. Carregar dados
    grafo = carregar_grafo(ARQUIVO_DADOS)
    print(f"Grafo carregado: {len(grafo)} usuários, {contar_arestas(grafo)} amizades.")

    # 3. Sortear usuários (sorted() garante a mesma ordem antes de sortear)
    random.seed(SEMENTE)
    origens = random.sample(sorted(grafo), AMOSTRA)

    # 2. Validar a implementação
    validar_com_networkx(grafo, origens)

    # 4. Rodar o BFS para cada usuário sorteado
    linhas = []
    for origem in origens:
        inicio = time.perf_counter()
        distancias = bfs_niveis(grafo, origem, N_MAX)
        tempo_ms = (time.perf_counter() - inicio) * 1000

        niveis = contar_por_nivel(distancias, N_MAX)
        linhas.append({
            "usuario": origem,
            "nivel_1": niveis[0],
            "nivel_2": niveis[1],
            "nivel_3": niveis[2],
            "tempo_ms": round(tempo_ms, 3),
        })

    tabela = pd.DataFrame(linhas)
    tabela.to_csv(PASTA_RESULTADOS / "exp1_por_usuario.csv", index=False)

    # 5a Tabela-resumo (vai para a seção Resultados do artigo)
    colunas = ["nivel_1", "nivel_2", "nivel_3", "tempo_ms"]
    resumo = tabela[colunas].agg(["mean", "median", "min", "max"]).round(2)
    resumo.index = ["Média", "Mediana", "Mínimo", "Máximo"]
    resumo.columns = ["Nível 1", "Nível 2", "Nível 3", "Tempo (ms)"]
    resumo.to_csv(PASTA_RESULTADOS / "exp1_resumo.csv")

    print("\nResumo por nível (usuários alcançados):")
    print(resumo.to_string())

    # Quantas vezes o nível 2 é maior que o nível 1 (mediana das razões)
    razao = (tabela["nivel_2"] / tabela["nivel_1"]).median()
    print(f"\nMediana da razão Nível 2 / Nível 1: {razao:.1f}x")

    # Percentual da rede alcançado em cada nível (acumulado)
    total = len(grafo)
    for n in range(1, N_MAX + 1):
        acumulado = tabela[[f"nivel_{i}" for i in range(1, n + 1)]].sum(axis=1).median()
        print(f"Até o nível {n}: mediana de {acumulado / total:.1%} da rede alcançada")

    # 5b Gráfico de barras com a mediana por nível
    medianas = tabela[["nivel_1", "nivel_2", "nivel_3"]].median()
    fig, ax = plt.subplots(figsize=(7, 4.5))
    barras = ax.bar(["Nível 1\n(amigos)", "Nível 2\n(amigos de amigos)", "Nível 3"],
                    medianas, color=["#4C72B0", "#DD8452", "#55A868"])
    ax.bar_label(barras, fmt="%.0f")
    ax.set_ylabel("Usuários alcançados (mediana)")
    ax.set_title(f"Crescimento da vizinhança por nível do BFS (n = {AMOSTRA})")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(PASTA_RESULTADOS / "exp1_grafico_niveis.png", dpi=200)

    print(f"\nArquivos salvos em: {PASTA_RESULTADOS}")


if __name__ == "__main__":
    main()
