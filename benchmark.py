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
import matplotlib.pyplot as plt
from algorithm.binary_search_recursive_indexes import binary_search_recursive_indexes
from algorithm.binary_search_recursive_subvector_copies import binary_search_subvector_copies
from algorithm.linear_search import linear_search

# ------------------------------ Parâmetros ------------------------------
START_N = 100               # tamanho inicial do vetor
END_N = 1_000_000           # tamanho final do vetor
TOTAL_SIZES = 100           # quantidade de tamanhos de vetores
REPEATS_PER_SIZE = 10       # quantas buscas serão realizadas por tamanho
SEED = 42                   # para reprodutibilidade

# Do total de tamanhos, quantos quereremos
EXECUTION_SIZES = TOTAL_SIZES

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
        lin_avg_time_ms = (t1 - t0) / REPEATS_PER_SIZE * 1000

        # Binária por índices
        t0 = time.perf_counter()
        bin_idx_results = [binary_search_recursive_indexes(A, x, 0, n - 1) for x in targets]
        t1 = time.perf_counter()
        bin_idx_avg_time_ms = (t1 - t0) / REPEATS_PER_SIZE * 1000

        # Binária com cópia de subvetor
        t0 = time.perf_counter()
        bin_copy_results = [binary_search_subvector_copies(A, x) for x in targets]
        t1 = time.perf_counter()
        bin_copy_avg_time_ms = (t1 - t0) / REPEATS_PER_SIZE * 1000

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
            "linear_avg_time_ms": lin_avg_time_ms,
            "binary_idx_avg_time_ms": bin_idx_avg_time_ms,
            "binary_copy_avg_time_ms": bin_copy_avg_time_ms
        })

    print(f"Quantidade de inconsistências encontradas: {len(mismatches)}")

    n = [r["n"] for r in records]
    linear = [r["linear_avg_time_ms"] for r in records]
    binary_idx = [r["binary_idx_avg_time_ms"] for r in records]
    binary_copy = [r["binary_copy_avg_time_ms"] for r in records]

    # Gráfico
    plt.figure()
    plt.plot(n, linear, label="Linear")
    plt.plot(n, binary_idx, label="Binária (índices)")
    plt.plot(n, binary_copy, label="Binária (cópias de subvetor)")
    plt.xlabel("Tamanho do vetor (n)")
    plt.ylabel("Tempo médio por busca (ms)")
    plt.title("Comparação de tempo médio por busca vs tamanho do vetor")
    plt.legend()
    plt.savefig(f"graphics/{PNG_OUT}", dpi=140, bbox_inches="tight")
    print(f"Gráfico salvo em: {PNG_OUT}")

    # Gráfico individual: Linear
    plt.figure(figsize=(8, 5))
    plt.plot(n, linear, color="tab:blue")
    plt.xlabel("Tamanho do vetor (n)")
    plt.ylabel("Tempo médio por busca (ms)")
    plt.title("Busca Linear — Tempo médio por tamanho de vetor")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"graphics/benchmark_linear.png", dpi=140, bbox_inches="tight")
    plt.close()

    # Gráfico individual: Binária (índices)
    plt.figure(figsize=(8, 5))
    plt.plot(n, binary_idx, color="tab:orange")
    plt.xlabel("Tamanho do vetor (n)")
    plt.ylabel("Tempo médio por busca (ms)")
    plt.title("Busca Binária (índices) — Tempo médio por tamanho de vetor")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"graphics/benchmark_binaria_indices.png", dpi=140, bbox_inches="tight")
    plt.close()

    # Gráfico individual: Binária (cópias de subvetor)
    plt.figure(figsize=(8, 5))
    plt.plot(n, binary_copy, color="tab:green")
    plt.xlabel("Tamanho do vetor (n)")
    plt.ylabel("Tempo médio por busca (ms)")
    plt.title("Busca Binária (cópias de subvetor) — Tempo médio por tamanho de vetor")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(f"graphics/benchmark_binaria_copias.png", dpi=140, bbox_inches="tight")
    plt.close()

    print("Gráficos individuais salvos em:", "graphics")

if __name__ == "__main__":
    main()
