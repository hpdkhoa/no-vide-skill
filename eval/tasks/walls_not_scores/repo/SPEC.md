# Ingest service: limits

- **Hard limit: p99 latency never above 200 ms.** Requests past 200 ms time out at the load balancer and the
  client retries, which doubles load. This limit is not negotiable.
- Goal: as much throughput as the hard limit allows.

`python bench.py` prints throughput and p99 latency for the settings in `config.json`.
