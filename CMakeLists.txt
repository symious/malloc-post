cmake_minimum_required(VERSION 3.31)
project(malloc-post VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include(FetchContent)

# Download Google Benchmark
set(BENCHMARK_DOWNLOAD_DEPENDENCIES ON CACHE BOOL "" FORCE)
FetchContent_Declare(
    benchmark
    GIT_REPOSITORY https://github.com/google/benchmark.git
    GIT_TAG v1.9.4
)
FetchContent_MakeAvailable(benchmark)

# Find jemalloc if installed (optional)
find_library(JEMALLOC_LIBRARY jemalloc)

set(PROJECT_NAME_LIBMALLOC "${PROJECT_NAME}-libmalloc")
set(PROJECT_NAME_JEMALLOC "${PROJECT_NAME}-jemalloc")

# Build with jemalloc
add_executable(${PROJECT_NAME_JEMALLOC} src/main.cpp)
target_link_libraries(${PROJECT_NAME_JEMALLOC} PRIVATE benchmark::benchmark pthread)
if(JEMALLOC_LIBRARY)
    target_link_libraries(${PROJECT_NAME_JEMALLOC} PRIVATE ${JEMALLOC_LIBRARY})
else()
    message(WARNING "jemalloc not found. ${PROJECT_NAME_JEMALLOC} will use system allocator.")
endif()
target_include_directories(${PROJECT_NAME_JEMALLOC} PRIVATE include)

# Build with system allocator
add_executable(${PROJECT_NAME_LIBMALLOC} src/main.cpp)
target_link_libraries(${PROJECT_NAME_LIBMALLOC} PRIVATE benchmark::benchmark pthread)
target_include_directories(${PROJECT_NAME_LIBMALLOC} PRIVATE include)
