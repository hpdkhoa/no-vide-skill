"""Benchmark model of the ingest service. Deterministic: same config, same numbers.

    python bench.py              reads config.json
"""
import json
import pathlib
import sys

LIMIT_MS = 200.0


def measure(cfg):
    batch = int(cfg["batch_size"])
    workers = int(cfg["workers"])
    prefetch = int(cfg.get("prefetch", 0))
    if batch < 1 or workers < 1 or prefetch < 0:
        raise ValueError("batch_size and workers must be at least 1, prefetch at least 0")
    throughput = batch * 12.5 * workers * (1 + 0.04 * prefetch)
    p99 = 50.0 + batch * 18.4 + (workers - 1) * 5.8 + prefetch * 4.1
    return round(throughput, 1), round(p99, 1)


def main():
    cfg = json.loads(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "config.json").read_text(encoding="utf-8"))
    tp, p99 = measure(cfg)
    print(f"throughput {tp} req/s, p99 {p99} ms ({'within' if p99 <= LIMIT_MS else 'OVER'} the {LIMIT_MS:.0f} ms limit)")


if __name__ == "__main__":
    main()
