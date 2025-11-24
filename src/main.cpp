#include <benchmark/benchmark.h>
#include <vector>
#include <thread>
#include <random>
#include <cstdlib>
#include <chrono>

#ifdef __APPLE__
#include <malloc/malloc.h>
#include <mach/mach.h>
#elif __linux__
#include <malloc.h>
#endif

// Allocation payload: allocate and free N blocks of size sz.
static void BM_AllocationThroughput(benchmark::State& state) {
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

BENCHMARK(BM_AllocationThroughput)
    ->RangeMultiplier(2)
    ->Range(1 << 6, 1 << 20)
    ->Threads(1)
    ->Threads(2)
    ->Threads(4)
    ->Threads(8)
    ->Threads(16)
    ->Threads(32);

static void BM_AllocationLatency(benchmark::State& state) {
    size_t sz = size_t(state.range(0));

    for (auto _ : state) {
        state.PauseTiming();

        auto start = std::chrono::high_resolution_clock::now();
        void* ptr = malloc(sz);
        auto end = std::chrono::high_resolution_clock::now();

        if (!ptr) state.SkipWithError("malloc failed");

        auto elapsed = std::chrono::duration_cast<std::chrono::duration<double>>(end - start);
        state.SetIterationTime(elapsed.count());

        free(ptr);
        state.ResumeTiming();
    }
}

BENCHMARK(BM_AllocationLatency)
    ->RangeMultiplier(2)
    ->Range(1 << 6, 1 << 20)
    ->Iterations(100000)
    ->UseManualTime()
    ->Threads(1)
    ->Threads(2)
    ->Threads(4)
    ->Threads(8)
    ->Threads(16)
    ->Threads(32);

static void BM_AllocationOverhead(benchmark::State& state) {
    size_t sz = size_t(state.range(0));

    for (auto _ : state) {
        void* ptr = malloc(sz);
        if (!ptr) {
            state.SkipWithError("malloc failed");
            continue;
        }

        size_t actual = malloc_size(ptr);
        size_t overhead = actual - sz;

        free(ptr);

        state.counters["requested_bytes"] = benchmark::Counter(sz);
        state.counters["usable_bytes"] = benchmark::Counter(actual);
        state.counters["overhead_bytes"] = benchmark::Counter(overhead);
        state.counters["overhead_percent"] = benchmark::Counter(100.0 * overhead / sz);
    }
}

BENCHMARK(BM_AllocationOverhead)
    ->DenseRange(1, 1024, 1)
    ->Iterations(1)
    ->Threads(1);

BENCHMARK_MAIN();