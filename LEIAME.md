# Experimento: BFS na recomendação de conexões em redes sociais

Experimento prático do artigo *"A utilização do algoritmo BFS pelas redes sociais na recomendação de conexões"*.

## Passo a passo para rodar

### 1. Instalar o Python e as bibliotecas
Use Python 3.9 ou mais recente. No terminal, dentro desta pasta:

```bash
pip install -r requirements.txt
```

### 2. Baixar o dataset
1. Acesse: https://snap.stanford.edu/data/ego-Facebook.html
2. Baixe o arquivo **facebook_combined.txt.gz**
3. Coloque-o na pasta `dados/` **sem descompactar**

Confira: o experimento 1 deve imprimir **4039 usuários e 88234 amizades**.

### 3. Testar o BFS com o exemplo do artigo
```bash
python bfs.py
```
A saída deve recomendar a Eve (2 amigos em comum) e o Dave (1), igual à tabela da seção 5 do artigo.

### 4. Rodar os experimentos
```bash
python experimento1_niveis.py      
python experimento2_validacao.py   
```

### 5. Pegar os resultados
Tudo fica na pasta `resultados/`:

| Arquivo | O que é | Onde usar |
|---|---|---|
| `exp1_resumo.csv` | Média/mediana de usuários por nível e tempo | Tabela em Resultados |
| `exp1_grafico_niveis.png` | Gráfico do crescimento por nível | Figura em Resultados + slide |
| `exp1_por_usuario.csv` | Dados brutos de cada usuário | Apêndice (opcional) |
| `exp2_resumo.csv` | Precisão, revocação e taxa de acerto (BFS vs. aleatório) | Tabela em Resultados |
| `exp2_grafico_validacao.png` | Gráfico BFS vs. aleatório | Figura em Resultados + slide |
| `exp2_por_repeticao.csv` | Resultado de cada repetição | Apêndice (opcional) |

## O que cada experimento mede

**Experimento 1: explosão por níveis.** Sorteia 100 usuários e conta quantas pessoas o BFS alcança nos níveis 1, 2 e 3. Antes, confere se o BFS implementado dá o mesmo resultado da biblioteca NetworkX, o que valida a implementação.

**Experimento 2: validação das recomendações (link prediction).** Esconde 10% das amizades, gera as 10 melhores recomendações de cada usuário pelo BFS e verifica quantas amizades escondidas foram "redescobertas". Compara com recomendações aleatórias. Repete 5 vezes com sementes diferentes e calcula média e desvio-padrão.

- **Precisão@10**: dos 10 recomendados, quantos eram amizades reais
- **Revocação@10**: das amizades escondidas, quantas foram recuperadas
- **Taxa de acerto**: % de usuários com pelo menos 1 acerto

## Reprodutibilidade
As sementes aleatórias são fixas (`SEMENTE = 42`), então rodar de novo dá exatamente o mesmo resultado. Cite isso na Metodologia.

## Dica para a Discussão
Numa rede pequena, o nível 3 pode ter **menos** usuários que o nível 2, porque a rede "acaba" (quase todo mundo já foi alcançado). Isso não é um erro: é o efeito de mundo pequeno. Compare com redes de bilhões de usuários, onde o nível 3 continua crescendo.

## Referência do dataset (ABNT)
LESKOVEC, Jure; KREVL, Andrej. **SNAP Datasets**: Stanford Large Network Dataset Collection. [*S. l.*], 2014. Disponível em: https://snap.stanford.edu/data. Acesso em: dia mês. ano.

McAULEY, Julian; LESKOVEC, Jure. Learning to discover social circles in ego networks. *In*: ADVANCES IN NEURAL INFORMATION PROCESSING SYSTEMS (NIPS), 2012. **Proceedings** [...]. 2012.
