cmake_minimum_required(VERSION 3.15)

project(malloc-post
    VERSION 0.1.0
    LANGUAGES CXX
)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add executable target
add_executable(${PROJECT_NAME}
    src/main.cpp
)

# Include directories for headers
target_include_directories(${PROJECT_NAME} PRIVATE include)
