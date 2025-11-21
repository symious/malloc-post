#!/bin/bash

set -euo pipefail

cmake --build build

MALLOCS=(libmalloc jemalloc)
for malloc in "${MALLOCS[@]}"; do
  ./build/malloc-post-${malloc} --benchmark_out=results/${malloc}.json
done

python3 benchmark_analysis.py
