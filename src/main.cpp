#include <iostream>

#include <benchmark/benchmark.h>

// A simple benchmark function
static void BM_StringCreation(benchmark::State& state) {
  for (auto _ : state) {
    std::string empty_string;
  }
}
BENCHMARK(BM_StringCreation);

BENCHMARK_MAIN();