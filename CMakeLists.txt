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

# Add executable target
add_executable(${PROJECT_NAME}
    src/main.cpp
)

# Include directories for headers
target_link_libraries(${PROJECT_NAME} PRIVATE benchmark::benchmark pthread)
target_include_directories(${PROJECT_NAME} PRIVATE include)
