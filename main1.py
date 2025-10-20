import time
import random
import argparse

from algorithm.linear_search import linear_search
from algorithm.binary_search_recursive_subvector_copies import binary_search_subvector_copies
from algorithm.binary_search_recursive_indexes import binary_search_recursive_indexes

REPEATS = 10


def bench(fn, *, repeats: int) -> float:
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    end = time.perf_counter()
    return end - start

def main():
    # Wrappers que executam uma ÚNICA busca (para somarmos várias execuções fairness)
    calls = []

    def call_linear():
        return linear_search(A, x)
    calls.append(("linear_search", call_linear))
    def call_bin_idx():
        return binary_search_recursive_indexes(A, x, 0, len(A) - 1)
    calls.append(("binary_search_recursive_indexes", call_bin_idx))
    def call_bin_slice():
        return binary_search_subvector_copies(A, x)
    calls.append(("binary_search_subvector_copies", call_bin_slice))

    # Comparar respostas.
    results = {name: fn() for name, fn in calls}
    if len(set(results.values())) != 1:
        print("Aviso: algoritmos retornaram índices diferentes:")
        for name, idx in results.items():
            print(f"  - {name}: {idx}")
    else:
        print(f"Índice retornado por todos: {next(iter(results.values()))}")

    # Medição
    print(f"\nEntrada: n={n}, alvo x={x}")
    timings = []
    for name, fn in calls:
        total = bench(fn, repeats=args.repeats)
        per_call = total / args.repeats
        timings.append((name, total, per_call))

    # Exibição
    print("\nTempos (segundos):")
    for name, total, per_call in timings:
        print(f"- {name:32s} total={total:9.6f}s  médio/chamada={per_call*1e6:9.2f}µs")


if __name__ == "__main__":
    main()
