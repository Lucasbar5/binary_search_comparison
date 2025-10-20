#!/usr/bin/env python3
"""
Benchmark de buscas: linear vs. binária (índices) vs. binária (cópias de subvetor).

- Gera 100 tamanhos igualmente espaçados entre 100 e 1_000_000 (parametrizável).
- Para cada tamanho, executa 10 buscas de alvos aleatórios (parametrizável) e
  mede o tempo médio por busca para cada algoritmo.
- Valida se todos os algoritmos retornam o mesmo resultado em cada consulta.
- Salva CSV e gráfico em disco.
"""

import random
import time
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------- Algoritmos fornecidos (com 1 fix) ----------------------

def binary_search_recursive_indexes(A, x, i, j):
    if j < i:
        return -1
    mid = (i + j) // 2

    if x == A[mid]:
        return mid
    elif x < A[mid]:
        return binary_search_recursive_indexes(A, x, i, mid-1)
    else:
        return binary_search_recursive_indexes(A, x, mid+1, j)

def binary_search_subvector_copies(A, x):
    n = len(A)
    if n <= 0:  # fix: impedir A[-1] quando lista vazia
        return -1
    mid = (0 + n - 1) // 2
    if x == A[mid]:
        return mid
    elif x < A[mid]:
        return binary_search_subvector_copies(A[:mid], x)
    else:
        result = binary_search_subvector_copies(A[mid+1:], x)
        if result != -1:
            return result + mid + 1
        else:
            return -1

def linear_search(A, x):
    for i in range(0, len(A)):
        if A[i] == x:
            return i
    return -1

# ------------------------------ Parâmetros ------------------------------
START_N = 100
END_N = 1_000_000
TOTAL_SIZES = 100           # 100 tamanhos igualmente espaçados
REPEATS_PER_SIZE = 10       # 10 alvos por tamanho
SEED = 42                   # para reprodutibilidade

# Para um "modo rápido" (ex.: testes), defina EXECUTION_SIZES < TOTAL_SIZES
EXECUTION_SIZES = TOTAL_SIZES

CSV_OUT = "busca_benchmark_resultados.csv"
PNG_OUT = "busca_benchmark_grafico.png"

# ------------------------------- Execução -------------------------------

def main():
    rng = random.Random(SEED)
    step = (END_N - START_N) // (TOTAL_SIZES - 1)
    all_sizes = [START_N + i * step for i in range(TOTAL_SIZES)]
    sizes = all_sizes[:EXECUTION_SIZES]

    records = []
    mismatches = []

    for n in sizes:
        A = list(range(n))  # vetor ordenado 0..n-1 (pré-condição da binária)
        # Sorteia alvos em um range mais largo para incluir casos de "não encontrado"
        targets = [rng.randint(-n // 2, (3 * n) // 2) for _ in range(REPEATS_PER_SIZE)]

        # Linear
        t0 = time.perf_counter()
        lin_results = [linear_search(A, x) for x in targets]
        t1 = time.perf_counter()
        lin_avg = (t1 - t0) / REPEATS_PER_SIZE

        # Binária por índices
        t0 = time.perf_counter()
        bin_idx_results = [binary_search_recursive_indexes(A, x, 0, n - 1) for x in targets]
        t1 = time.perf_counter()
        bin_idx_avg = (t1 - t0) / REPEATS_PER_SIZE

        # Binária com cópia de subvetor
        t0 = time.perf_counter()
        bin_copy_results = [binary_search_subvector_copies(A, x) for x in targets]
        t1 = time.perf_counter()
        bin_copy_avg = (t1 - t0) / REPEATS_PER_SIZE

        # Verificação dos resultados
        for x, r1, r2, r3 in zip(targets, lin_results, bin_idx_results, bin_copy_results):
            if not (r1 == r2 == r3):
                mismatches.append({
                    "n": n,
                    "x": x,
                    "linear": r1,
                    "binary_indexes": r2,
                    "binary_subvector": r3
                })

        records.append({
            "n": n,
            "linear_avg_time_s": lin_avg,
            "binary_idx_avg_time_s": bin_idx_avg,
            "binary_copy_avg_time_s": bin_copy_avg
        })

    df = pd.DataFrame(records)
    df.to_csv(CSV_OUT, index=False)
    print(f"CSV salvo em: {CSV_OUT}")
    print(f"Inconsistências encontradas: {len(mismatches)}")

    # Gráfico
    plt.figure()
    plt.plot(df["n"], df["linear_avg_time_s"], label="Linear")
    plt.plot(df["n"], df["binary_idx_avg_time_s"], label="Binária (índices)")
    plt.plot(df["n"], df["binary_copy_avg_time_s"], label="Binária (cópias de subvetor)")
    plt.xlabel("Tamanho do vetor (n)")
    plt.ylabel("Tempo médio por busca (s)")
    plt.title("Comparação de tempo médio por busca vs tamanho do vetor")
    plt.legend()
    plt.savefig(PNG_OUT, dpi=140, bbox_inches="tight")
    print(f"Gráfico salvo em: {PNG_OUT}")

if __name__ == "__main__":
    main()
