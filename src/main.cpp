#include <benchmark/benchmark.h>
#include <vector>
#include <thread>
#include <random>
#include <cstdlib>
#include <chrono>
#include <malloc/malloc.h>

static void BM_AllocationThroughput(benchmark::State& state) {
    size_t sz = size_t(state.range(0));
    size_t n = 1000;

    std::vector<void*> ptrs(n);

    for (auto _ : state) {
        std::mt19937 rng(std::hash<std::thread::id>{}(std::this_thread::get_id()));
        std::uniform_int_distribution<int> dist(0, n - 1);

        for (size_t i = 0; i < n; ++i) {
            ptrs[i] = malloc(sz);
            if (!ptrs[i]) state.SkipWithError("malloc failed");
        }
        benchmark::DoNotOptimize(ptrs);

        for (size_t i = 0; i < n; ++i) {
            int j = dist(rng);
            free(ptrs[j]);
            ptrs[j] = malloc(sz);
        }

        for (size_t i = 0; i < n; ++i) {
            free(ptrs[i]);
        }
    }

    state.SetItemsProcessed(state.iterations() * n);
}

BENCHMARK(BM_AllocationThroughput)
    ->RangeMultiplier(2)
    ->Range(1 << 1, 1 << 25)
    ->Iterations(1000)
    ->Threads(1)
    ->Threads(2)
    ->Threads(4)
    ->Threads(8);

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
    ->Range(1 << 1, 1 << 25)
    ->Iterations(1000)
    ->UseManualTime()
    ->Threads(1)
    ->Threads(2)
    ->Threads(4)
    ->Threads(8);

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
    ->DenseRange(1024, 2048, 2)
    ->DenseRange(2048, 4096, 4)
    ->DenseRange(4096, 8192, 8)
    ->DenseRange(8192, 16384, 16)
    ->DenseRange(16384, 32768, 32)
    ->DenseRange(32768, 65536, 64)
    ->DenseRange(65536, 131072, 128)
    ->DenseRange(131072, 262144, 256)
    ->DenseRange(262144, 524288, 512)
    ->DenseRange(524288, 1048576, 1024)
    ->DenseRange(1048576, 2097152, 2048)
    ->DenseRange(2097152, 4194304, 4096)
    ->DenseRange(4194304, 8388608, 8192)
    ->DenseRange(8388608, 16777216, 16384)
    ->DenseRange(16777216, 33554432, 32768)
    ->DenseRange(33554432, 67108864, 65536)
    ->DenseRange(67108864, 134217728, 131072)
    ->DenseRange(134217728, 268435456, 262144)
    ->DenseRange(268435456, 536870912, 524288)
    ->DenseRange(536870912, 1073741824, 1048576)
    ->Iterations(1)
    ->Threads(1);

BENCHMARK_MAIN();