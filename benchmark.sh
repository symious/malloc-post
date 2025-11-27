#!/bin/bash

set -euo pipefail

cmake --build build


run_allocation_throughput_benchmark() {
  local size=$1
  local threads=$2
  rm -f /tmp/BM_AllocationThroughput.log
  echo "Running allocation throughput benchmark for ${MALLOC} with ${size} size, ${threads} threads"
  ${executable} --benchmark_filter="BM_AllocationThroughput/${size}/iterations:1000/threads:${threads}" \
    --benchmark_out="results/${MALLOC}_AllocationThroughput_${size}_${threads}.json" \
    > /dev/null 2>> /tmp/BM_AllocationThroughput.log
}

run_allocation_latency_benchmark() {
  local size=$1
  local threads=$2
  rm -f /tmp/BM_AllocationLatency.log
  echo "Running allocation latency benchmark for ${MALLOC} with ${size} size, ${threads} threads"
  ${executable} --benchmark_filter="BM_AllocationLatency/${size}/iterations:1000000/manual_time/threads:${threads}" \
    --benchmark_out="results/${MALLOC}_AllocationLatency_${size}_${threads}.json" \
    > /dev/null 2>> /tmp/BM_AllocationLatency.log
}

run_allocation_overhead_benchmark() {
  rm -f /tmp/BM_AllocationOverhead.log
  echo "Running allocation overhead benchmark for ${MALLOC}"
  ${executable} --benchmark_filter="BM_AllocationOverhead" \
    --benchmark_out="results/${MALLOC}_AllocationOverhead.json" \
    > /dev/null 2>> /tmp/BM_AllocationOverhead.log
}

executable_prefix="./build/malloc-post-benchmark-"

for executable in ${executable_prefix}*; do
  MALLOC="${executable#./build/malloc-post-benchmark-}"
  for threads in 1 2 4 8; do
    for size in {1..22}; do
      run_allocation_throughput_benchmark $((2**size)) ${threads}
    done
  done
  for threads in 1 2 4 8; do
    for size in {1..22}; do
      run_allocation_latency_benchmark $((2**size)) ${threads}
    done
  done
  run_allocation_overhead_benchmark
done

run_rss_benchmark() {
  local threads=$1
  local iterations=$2
  local size=$3
  local count=$4
  echo "Running RSS measurements for ${MALLOC} with ${threads} threads, ${iterations} iterations, ${size} size, ${count} count"
  ${executable} ${threads} ${iterations} ${size} ${count} > results/${MALLOC}_${threads}_${iterations}_${size}_${count}.csv
}

executable_prefix="./build/malloc-post-rss-"

for executable in ${executable_prefix}*; do
  MALLOC="${executable#./build/malloc-post-rss-}"
  echo "Running RSS measurements for ${MALLOC}"
  for threads in 1 2 4 8; do
    run_rss_benchmark ${threads} 1000 1024 10
  done
  for iterations in 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000; do
    run_rss_benchmark 4 ${iterations} 1024 10
  done
  for size in 1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576; do
    run_rss_benchmark 4 100 ${size} 10
  done
done

python3 benchmark_analysis.py
