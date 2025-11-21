## Building

```bash
brew install jemalloc
```

```bash
mkdir build
cmake -S . -B build
cmake --build build
```

## Benchmarking

```bash
build/malloc-post-system
build/malloc-post-jemalloc
```