#include <malloc/malloc.h>
#include <mach/mach.h>
#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <cstring>

size_t get_rss_bytes() {
    struct mach_task_basic_info info;
    mach_msg_type_number_t count = MACH_TASK_BASIC_INFO_COUNT;
    if (task_info(mach_task_self(), MACH_TASK_BASIC_INFO,
                  (task_info_t)&info, &count) == KERN_SUCCESS) {
        return info.resident_size;
    }
    return 0;
}

std::atomic<bool> should_stop(false);

void worker_thread(size_t num_pointers, size_t pointer_size) {
    std::vector<void*> pointers;
    pointers.reserve(num_pointers);

    while (!should_stop.load()) {
        if (pointers.size() < num_pointers) {
            void* ptr = malloc(pointer_size);
            if (ptr != nullptr) {
                memset(ptr, 0, pointer_size);
                pointers.push_back(ptr);
            }
        } else {
            size_t idx = rand() % pointers.size();
            free(pointers[idx]);
            void* ptr = malloc(pointer_size);
            if (ptr != nullptr) {
                memset(ptr, 0, pointer_size);
                pointers[idx] = ptr;
            }
        }
    }

    for (void* ptr : pointers) {
        free(ptr);
    }
}

void print_usage(const char* program_name) {
    std::cerr << "Usage: " << program_name
              << " <num_threads> <num_pointers> <pointer_size> <duration_seconds>\n";
    std::cerr << "  num_threads: Number of worker threads to spawn\n";
    std::cerr << "  num_pointers: Number of pointers each thread maintains\n";
    std::cerr << "  pointer_size: Size of each allocation in bytes\n";
    std::cerr << "  duration_seconds: How long to run the workload\n";
}

int main(int argc, char* argv[]) {
    if (argc != 5) {
        print_usage(argv[0]);
        return 1;
    }

    int num_threads = std::atoi(argv[1]);
    size_t num_pointers = std::atoll(argv[2]);
    size_t pointer_size = std::atoll(argv[3]);
    int duration_seconds = std::atoi(argv[4]);

    if (num_threads <= 0 || num_pointers <= 0 || pointer_size <= 0 || duration_seconds <= 0) {
        std::cerr << "Error: All arguments must be positive numbers\n";
        print_usage(argv[0]);
        return 1;
    }

    std::cout << "elapsed_ms,rss_bytes\n" << std::flush;

    std::vector<std::thread> threads;
    threads.reserve(num_threads);

    auto start_time = std::chrono::steady_clock::now();

    size_t rss = get_rss_bytes();
    std::cout << "0," << rss << "\n" << std::flush;

    for (int i = 0; i < num_threads; ++i) {
        threads.emplace_back(worker_thread, num_pointers, pointer_size);
    }
    auto end_time = start_time + std::chrono::seconds(duration_seconds);

    while (std::chrono::steady_clock::now() < end_time) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(now - start_time).count();
        size_t rss = get_rss_bytes();
        std::cout << elapsed << "," << rss << "\n" << std::flush;
    }

    should_stop.store(true);

    for (auto& thread : threads) {
        thread.join();
    }

    std::this_thread::sleep_for(std::chrono::seconds(1));

    auto final_time = std::chrono::steady_clock::now();
    auto final_elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
        final_time - start_time).count();
    size_t final_rss = get_rss_bytes();

    std::cout << final_elapsed << "," << final_rss << "\n" << std::flush;

    return 0;
}

