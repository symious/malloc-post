#!/bin/bash

set -euo pipefail

cmake --build build

executable_prefix="./build/malloc-post-"

for executable in ${executable_prefix}*; do
  MALLOC="${executable#./build/malloc-post-}"
  echo "Running benchmarks for ${MALLOC}"
  ${executable} --benchmark_out=results/${MALLOC}.json > /dev/null #results/${MALLOC}.txt
done

python3 benchmark_analysis.py
