#include <benchmark/benchmark.h>
#include <vector>
#include <thread>
#include <random>
#include <cstdlib>

// Allocation payload: allocate and free N blocks of size sz.
static void BM_Throughput(benchmark::State& state) {
    // Size of each allocation
    size_t sz = size_t(state.range(0));
    // Number of allocations per thread per iteration
    size_t n = 1000;

    std::vector<void*> ptrs(n);

    for (auto _ : state) {
        // Simple per-thread RNG to spread allocations
        std::mt19937 rng(std::hash<std::thread::id>{}(std::this_thread::get_id()));
        std::uniform_int_distribution<int> dist(0, n - 1);

        // Allocate
        for (size_t i = 0; i < n; ++i) {
            ptrs[i] = malloc(sz);
            if (!ptrs[i]) state.SkipWithError("malloc failed");
        }
        benchmark::DoNotOptimize(ptrs);

        // Optional: Random access pattern to stress allocator
        for (size_t i = 0; i < n; ++i) {
            int j = dist(rng);
            free(ptrs[j]);
            ptrs[j] = malloc(sz);
        }

        // Free everything
        for (size_t i = 0; i < n; ++i) {
            free(ptrs[i]);
        }
    }
    state.SetItemsProcessed(state.iterations() * n);
}

BENCHMARK(BM_Throughput)
    ->RangeMultiplier(2)
    ->Range(1 << 6, 1 << 20)
    ->Threads(1)
    ->Threads(2)
    ->Threads(4)
    ->Threads(8)
    ->Threads(16)
    ->Threads(32);;

BENCHMARK_MAIN();