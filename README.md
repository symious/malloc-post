## Building

```bash
brew install mimalloc jemalloc #tcmalloc #hoard #dmalloc
```

```bash
mkdir build
cmake -S . -B build
cmake --build build
```

## Benchmarking

```bash
./benchmark.sh
```