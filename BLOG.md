---
title: malloc
published: false
description: 
tags: cpp
cover_image: 
---

- jemalloc widely used in high performance databases (C*, ClickHouse)
- compare different allocators
- compare throughput
- compare other metrics
  - memory footprint and overhead
  - memory fragmentation
  - latency
- compare tooling (debugging, profiling, etc.)
- compare jemalloc performance across different sizes with 8 threads
- TODO https://github.com/google/benchmark/issues/178

## Results

- Ratio for {'threads': 8, 'size': 1024} {'implementation': 'tcmalloc'} / {'implementation': 'libmalloc'}: 1.3716038584770054 items_per_second/items_per_second
- Ratio for {'threads': 8, 'size': 1048576} {'implementation': 'tcmalloc'} / {'implementation': 'libmalloc'}: 20.009644120772688 items_per_second/items_per_second


For a database, the allocator choice affects throughput, latency tails, memory footprint, and operational behavior over long uptimes, so the key is to match the allocator’s behavior to your workload and SLOs.​

Workload and allocation patterns
Characterize the typical allocation sizes (tiny, small, large), object lifetimes, and locality patterns of your DB (buffer cache, query executor, background threads, etc.), since different allocators optimize for different size classes and lifetimes.​

High‑throughput DBs often show that the same code compiled against different allocators can vary by 10–50% in query throughput and latency, depending on the allocator’s fit to the workload.​

Throughput under concurrency
For many‑core servers, lock contention in the allocator can dominate, so you want per‑thread or sharded heaps and low cross‑thread contention; jemalloc, tcmalloc, mimalloc and similar “high‑perf” allocators were designed for this.​

Micro‑ and macro‑benchmarks on MySQL, LevelDB, RocksDB, and other engines consistently show better scalability from jemalloc/tcmalloc vs classic glibc malloc at high thread counts, with notably higher QPS and better parallel speedup.​

Latency and tail behavior
Look at p95–p99 latency impact, not just average throughput, because some allocators introduce long internal pauses (global locks, arena rebalancing, page reclamation) that show up as query latency spikes.​

Experimental studies on OLAP/OLTP workloads show that certain glibc malloc versions can have much worse tail latencies than jemalloc or mimalloc under bursty request loads, even when median latency is similar.​

Fragmentation and memory footprint
Long‑running DBs with mixed allocation sizes are prone to fragmentation; allocators differ significantly here, with some trading higher virtual and RSS usage for speed, and others being more compact but slightly slower.​

In practice, swapping from a default malloc to jemalloc or tcmalloc has reduced DB memory usage by multiple GiB on 16 GiB systems, but some experiments also show jemalloc consuming more memory than glibc in specific analytic workloads, so this must be measured for your case.​

Returning memory to the OS
Some allocators are aggressive about keeping arenas and pages for reuse and only reluctantly return memory to the OS, which can be good for performance but bad for multi‑tenant environments or dynamic workloads.​

Others (or specific configuration modes) are more eager to hand memory back to the kernel, improving coexistence with other services at the cost of more page faults and occasional allocator work spikes.​

Threading model and pools
If the DB uses mostly static worker threads (typical for thread pools), allocators with per‑thread caches (like jemalloc’s per‑thread arenas) work very well and minimize contention.​

If threads are frequently created and destroyed, an allocator whose design tolerates or optimizes for shifting thread ownership of caches (e.g., tcmalloc’s shared central cache model) can behave better and avoid cache blow‑up or many cold per‑thread heaps.​

Introspection and tuning knobs
Modern allocators expose detailed stats and profiling (fragmentation, size‑class usage, per‑arena counts), which are extremely useful for diagnosing odd memory behavior in a production DB.​

Many provide tunables for arena count, decay policies, large allocation thresholds, and security hardening; being able to tune these without code changes is valuable for tailoring to different deployments.​

Integration with DB design
For core, high‑traffic subsystems (buffer pool, query execution, caching), consider using custom arenas/pools on top of the general allocator so hot paths avoid generic malloc as much as possible.​

Where lifetimes are structured (per‑query, per‑transaction, per‑snapshot), region/arena allocators that free in bulk at scope end can outclass any general‑purpose malloc in both speed and fragmentation, reserving the global allocator mainly for long‑lived structures.​

Stability, maturity, and ecosystem usage
Prefer allocators that are widely deployed in similar production systems (e.g., major DBs, caches, cloud services) because their corner cases have been exercised and patched.​

Projects like Redis, Varnish and large cloud services have reported significant improvements in stability and resource usage after switching from the system malloc to jemalloc or tcmalloc, which is a useful signal when choosing.​

Operational considerations
Ensure observability: can you attribute leaks or runaway growth to subsystems, and does the allocator’s tooling integrate with your existing profiling and monitoring stack.​

Consider security and hardening options (guard pages, randomized layouts, secure modes) and balance them against performance overhead for your threat model and deployment environment.​

Evaluation methodology
Always benchmark your specific DB workload with candidate allocators using realistic schemas, queries, and concurrency, capturing throughput, p95/p99 latency, RSS/VSZ, fragmentation metrics, and page‑fault behavior over long uptimes.​

Test behavior under overload and pathological patterns (e.g., many concurrent connections doing allocations, large batch loads, heavy churn) to catch allocator‑induced stalls or memory bloat before committing to one choice.​