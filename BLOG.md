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
