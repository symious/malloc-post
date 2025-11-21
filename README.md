## Building

```bash
brew tap emeryberger/hoard
brew install --HEAD emeryberger/hoard/libhoard
brew install mimalloc jemalloc
brew install gperftools # tcmalloc
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