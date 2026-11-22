import gzip
from collections import deque, defaultdict
from pathlib import Path

# Leitura do grafo
def carregar_grafo(caminho):
   
    caminho = Path(caminho)
    abrir = gzip.open if caminho.suffix == ".gz" else open

    grafo = defaultdict(set)
    with abrir(caminho, "rt") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if not linha or linha.startswith("#"):  
                continue
            u, v = map(int, linha.split())
            if u == v:  
                continue
            grafo[u].add(v)
            grafo[v].add(u)

    return dict(grafo)


def contar_arestas(grafo):
    return sum(len(amigos) for amigos in grafo.values()) // 2

# 2 BFS clássico limitado por profundidade
def bfs_niveis(grafo, origem, n_max):
    distancia = {origem: 0}  
    fila = deque([origem])  

    while fila:
        atual = fila.popleft()           
        if distancia[atual] >= n_max:    
            continue
        for vizinho in grafo.get(atual, ()):
            if vizinho not in distancia:  
                distancia[vizinho] = distancia[atual] + 1
                fila.append(vizinho)    

    return distancia


def contar_por_nivel(distancias, n_max):
    contagem = [0] * (n_max + 1)
    for d in distancias.values():
        contagem[d] += 1
    return contagem[1:]  

# 3. BFS adaptado para recomendação (amigos em comum)
def recomendar_conexoes(grafo, origem, top_k=None):
    amigos_diretos = grafo.get(origem, set())  
    amigos_em_comum = defaultdict(list)          

    for amigo in amigos_diretos:
        for candidato in grafo.get(amigo, ()):
            if candidato == origem or candidato in amigos_diretos:
                continue 
            amigos_em_comum[candidato].append(amigo)

    candidatos = [
        (candidato, len(intermediarios), intermediarios)
        for candidato, intermediarios in amigos_em_comum.items()
    ]
    candidatos.sort(key=lambda c: (-c[1], c[0]))

    return candidatos[:top_k] if top_k else candidatos

# Rode:  python bfs.py
if __name__ == "__main__":
    A, B, C, D, E, F = "Alice", "Bob", "Carol", "Dave", "Eve", "Frank"
    exemplo = {
        A: {B, C},
        B: {A, D, E},
        C: {A, E},
        D: {B, F},
        E: {B, C},
        F: {D},
    }

    print("Distâncias a partir de Alice:", bfs_niveis(exemplo, A, n_max=3))
    print("\nRecomendações para Alice:")
    for candidato, qtd, comuns in recomendar_conexoes(exemplo, A):
        print(f"  {candidato}: {qtd} amigo(s) em comum -> {sorted(comuns)}")
