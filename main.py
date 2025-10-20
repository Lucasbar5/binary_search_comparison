import time
import random
import argparse
from typing import List, Tuple

from algorithm.linear_search import linear_search
from algorithm.binary_search_recursive_subvector_copies import (
    binary_search_subvector_copies,
)
from algorithm.binary_search_recursive_indexes import (
    binary_search_recursive_indexes,
)


def bench_noargs(fn, *, repeats: int) -> float:
    start = time.perf_counter()
    for _ in range(repeats):
        fn()
    end = time.perf_counter()
    return end - start


def bench_targets(fn, targets: List[int]) -> float:
    start = time.perf_counter()
    for t in targets:
        fn(t)
    end = time.perf_counter()
    return end - start


def make_random_increasing_sequence(n: int, step_max: int = 10) -> List[int]:
    cur = random.randint(0, step_max)
    arr = [cur]
    for _ in range(1, n):
        cur += random.randint(1, step_max)
        arr.append(cur)
    return arr


def spaced_sizes(min_n: int, max_n: int, points: int) -> List[int]:
    if points <= 1:
        return [max_n]
    step = max(1, (max_n - min_n) // (points - 1))
    sizes = [min_n + i * step for i in range(points)]
    sizes[-1] = max_n
    return sizes


def interpolate_int(n: int, n_min: int, n_max: int, rep_min: int, rep_max: int) -> int:
    if n_max == n_min:
        return max(1, rep_max)
    rep = rep_min + (rep_max - rep_min) * (n - n_min) / (n_max - n_min)
    return max(1, int(round(rep)))


def single_run(n: int, repeats: int, target_mode: str | None, x_explicit: int | None):
    # Entrada: vetor ordenado [0, 1, 2, ..., n-1]
    A = list(range(n))

    if x_explicit is not None:
        if not (0 <= x_explicit < n):
            raise SystemExit("-x deve estar em [0, n-1] para este cenário.")
        x = x_explicit
    else:
        if target_mode == "first":
            x = 0
        elif target_mode == "mid":
            x = n // 2
        elif target_mode == "last":
            x = n - 1
        else:
            x = random.randrange(0, n)

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

    # Verificação de corretude (uma execução por algoritmo)
    results = {name: fn() for name, fn in calls}
    if len(set(results.values())) != 1:
        print("Aviso: algoritmos retornaram índices diferentes:")
        for name, idx in results.items():
            print(f"  - {name}: {idx}")
    else:
        print(f"Índice retornado por todos: {next(iter(results.values()))}")

    # Medição
    print(f"\nEntrada: n={n}, alvo x={x}, repetições={repeats}")
    timings = []
    for name, fn in calls:
        total = bench_noargs(fn, repeats=repeats)
        per_call = total / repeats
        timings.append((name, total, per_call))

    # Exibição
    print("\nTempos (segundos):")
    for name, total, per_call in timings:
        print(f"- {name:32s} total={total:9.6f}s  médio/chamada={per_call*1e6:9.2f}µs")


def sweep_run(
    min_n: int,
    max_n: int,
    points: int,
    repeats_at_min: int,
    repeats_at_max: int,
    csv_out: str,
    png_out: str | None,
    log_x: bool,
    log_y: bool,
):
    sizes = spaced_sizes(min_n, max_n, points)

    # Gera um único catálogo aleatório crescente do tamanho máximo e usa prefixos
    print(f"Gerando catálogo aleatório crescente com tamanho {max_n}...")
    base = make_random_increasing_sequence(max_n)

    # Wrappers por algoritmo (aceitam x como argumento)
    def wrap_linear(A):
        return lambda x: linear_search(A, x)

    def wrap_bin_idx(A):
        return lambda x: binary_search_recursive_indexes(A, x, 0, len(A) - 1)

    def wrap_bin_slice(A):
        return lambda x: binary_search_subvector_copies(A, x)

    algos = [
        ("linear_search", wrap_linear),
        ("binary_search_recursive_indexes", wrap_bin_idx),
        ("binary_search_subvector_copies", wrap_bin_slice),
    ]

    rows: List[Tuple[int, float, float, float]] = []
    # Medir tempos médios por tamanho
    for n in sizes:
        A = base[:n]
        reps = interpolate_int(n, min_n, max_n, repeats_at_min, repeats_at_max)
        # Mesmos alvos em comum para todos os algoritmos (produto aleatório existente)
        targets = [A[random.randrange(n)] for _ in range(reps)]

        per_algo_us = []
        for name, wrap in algos:
            fn = wrap(A)
            total = bench_targets(fn, targets)
            avg_us = (total / reps) * 1e6
            per_algo_us.append(avg_us)

        rows.append((n, per_algo_us[0], per_algo_us[1], per_algo_us[2]))
        print(
            f"n={n:>7d}  reps={reps:>4d}  avg_us: linear={per_algo_us[0]:9.2f}  idx={per_algo_us[1]:9.2f}  slice={per_algo_us[2]:9.2f}"
        )

    # Salva CSV
    with open(csv_out, "w", encoding="utf-8") as f:
        f.write("n,linear_search_us,binary_indexes_us,binary_slice_us\n")
        for n, l_us, bi_us, bs_us in rows:
            f.write(f"{n},{l_us:.6f},{bi_us:.6f},{bs_us:.6f}\n")
    print(f"Resultados salvos em {csv_out}")

    # Plot (se matplotlib disponível)
    if png_out is not None:
        try:
            import matplotlib.pyplot as plt

            xs = [r[0] for r in rows]
            ys_l = [r[1] for r in rows]
            ys_bi = [r[2] for r in rows]
            ys_bs = [r[3] for r in rows]

            plt.figure(figsize=(9, 6))
            plt.plot(xs, ys_l, label="Linear")
            plt.plot(xs, ys_bi, label="Binária (índices)")
            plt.plot(xs, ys_bs, label="Binária (subvetor)")
            plt.xlabel("Tamanho do catálogo (n)")
            plt.ylabel("Tempo médio por busca (µs)")
            plt.title("Busca em catálogo ordenado: tempo médio vs tamanho")
            if log_x:
                plt.xscale("log")
            if log_y:
                plt.yscale("log")
            plt.legend()
            plt.grid(True, which="both", ls=":", alpha=0.5)
            plt.tight_layout()
            plt.savefig(png_out, dpi=120)
            print(f"Gráfico salvo em {png_out}")
        except Exception as e:
            print(
                "Não foi possível gerar o gráfico automaticamente. Salvei o CSV. "
                "Se desejar o gráfico, instale matplotlib (pip install matplotlib)."
            )
            print(f"Detalhes: {e}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Compare tempos de busca (linear e binária). Modo único ou varredura."
        )
    )

    sub = parser.add_subparsers(dest="mode", required=False)

    # Modo 1: execução única (compatível com versão anterior)
    p_single = sub.add_parser("single", help="Executa medição para um único tamanho")
    p_single.add_argument("--n", type=int, default=10000, help="Tamanho do vetor ordenado")
    p_single.add_argument(
        "--repeats", type=int, default=500, help="Número de repetições por algoritmo"
    )
    p_single.add_argument(
        "--target",
        choices=["first", "mid", "last", "random"],
        default="last",
        help="Como escolher o alvo (valor existente)",
    )
    p_single.add_argument(
        "-x",
        type=int,
        default=None,
        help="Valor alvo explícito (se fornecido, ignora --target)",
    )

    # Modo 2: varredura em múltiplos tamanhos
    p_sweep = sub.add_parser(
        "sweep",
        help=(
            "Varre tamanhos entre 1e2 e 1e6 (ou custom) e salva CSV/gráfico"
        ),
    )
    p_sweep.add_argument("--min-n", type=int, default=100)
    p_sweep.add_argument("--max-n", type=int, default=1_000_000)
    p_sweep.add_argument("--points", type=int, default=100, help="Quantos tamanhos distintos")
    p_sweep.add_argument(
        "--repeats-at-min",
        type=int,
        default=200,
        help="Repetições para o menor n",
    )
    p_sweep.add_argument(
        "--repeats-at-max",
        type=int,
        default=1,
        help="Repetições para o maior n",
    )
    p_sweep.add_argument(
        "--csv-out", type=str, default="benchmark.csv", help="Caminho do CSV de saída"
    )
    p_sweep.add_argument(
        "--png-out",
        type=str,
        default="benchmark.png",
        help="Caminho do PNG (requer matplotlib). Use '' para desativar",
    )
    p_sweep.add_argument("--log-x", action="store_true", help="Usa escala log no eixo X")
    p_sweep.add_argument("--log-y", action="store_true", help="Usa escala log no eixo Y")

    args = parser.parse_args()

    if args.mode == "sweep":
        png_out = None if (args.png_out is None or args.png_out == "") else args.png_out
        sweep_run(
            min_n=args.min_n,
            max_n=args.max_n,
            points=args.points,
            repeats_at_min=args.repeats_at_min,
            repeats_at_max=args.repeats_at_max,
            csv_out=args.csv_out,
            png_out=png_out,
            log_x=args.log_x,
            log_y=args.log_y,
        )
    else:
        # default para compatibilidade: single
        n = getattr(args, "n", 10000)
        repeats = getattr(args, "repeats", 500)
        target = getattr(args, "target", "last")
        x_explicit = getattr(args, "x", None)
        single_run(n=n, repeats=repeats, target_mode=target, x_explicit=x_explicit)


if __name__ == "__main__":
    main()

