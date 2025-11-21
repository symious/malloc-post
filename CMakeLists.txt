cmake_minimum_required(VERSION 3.31)

project(malloc-post
    VERSION 0.1.0
    LANGUAGES CXX
)

include(FetchContent)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Download Google Benchmark
set(BENCHMARK_DOWNLOAD_DEPENDENCIES ON CACHE BOOL "" FORCE)
FetchContent_Declare(
        benchmark
        GIT_REPOSITORY https://github.com/google/benchmark.git
        GIT_TAG v1.9.4  # or the desired release tag
)
FetchContent_MakeAvailable(benchmark)

# Find jemalloc if installed, optional
find_library(JEMALLOC_LIBRARY jemalloc)
find_path(JEMALLOC_INCLUDE_DIR jemalloc/jemalloc.h)

# Define executable names in variables
set(EXEC_SYSTEM "${PROJECT_NAME}-libmalloc")
set(EXEC_JEMALLOC "${PROJECT_NAME}-jemalloc")

# System allocator executable
add_executable(${EXEC_SYSTEM}
    src/main.cpp
)
target_link_libraries(${EXEC_SYSTEM} PRIVATE benchmark::benchmark pthread)
target_include_directories(${EXEC_SYSTEM} PRIVATE include)

# Jemalloc allocator executable
add_executable(${EXEC_JEMALLOC}
    src/main.cpp
)
target_link_libraries(${EXEC_JEMALLOC} PRIVATE benchmark::benchmark pthread)

if(JEMALLOC_LIBRARY AND JEMALLOC_INCLUDE_DIR)
    target_include_directories(${EXEC_JEMALLOC} PRIVATE ${JEMALLOC_INCLUDE_DIR})
    target_link_libraries(${EXEC_JEMALLOC} PRIVATE ${JEMALLOC_LIBRARY})
else()
    message(WARNING "jemalloc not found. ${EXEC_JEMALLOC} will link without jemalloc.")
endif()

target_include_directories(${EXEC_JEMALLOC} PRIVATE include)