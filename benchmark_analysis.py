import json
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

grouped = defaultdict(list)
results_folder = 'results'

for filename in os.listdir(results_folder):
    if filename.endswith('.json'):
        filepath = os.path.join(results_folder, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for bm in data["benchmarks"]:
                bm_name = re.search(r"BM_(.+?)/", bm["name"]).group(1)
                implementation = os.path.splitext(filename)[0]
                enriched_benchmark = {
                    "bm_name": bm_name,
                    "implementation": implementation,
                    "size": int(re.findall(r'/(\d+)', bm["name"])[0]),
                    **bm
                }
                # {'bm_name': 'MallocFree_Multithreaded', 'implementation': 'system', 'size': 8192, 'name': 'BM_MallocFree_Multithreaded/8192/threads:8', 'family_index': 0, 'per_family_instance_index': 15, 'run_name': 'BM_MallocFree_Multithreaded/8192/threads:8', 'run_type': 'iteration', 'repetitions': 1, 'repetition_index': 0, 'threads': 8, 'iterations': 5712, 'real_time': 137789.86525395754, 'cpu_time': 137266.98179271698, 'time_unit': 'ns', 'items_per_second': 7285073.124941815}
                grouped[implementation + "_" + bm_name].append(enriched_benchmark)

def plot_data(y_label):
    for result_name, data in grouped.items():
        # Organize data by library
        grouped_data = defaultdict(list)
        for entry in data:
            if y_label in entry:
                grouped_data[entry["size"]].append((entry["threads"], entry[y_label]))

        if not grouped_data:
            continue

        plt.figure(figsize=(10,6))
        for library, points in grouped_data.items():
            # Sort points by size for a clean plot
            points.sort(key=lambda x: x[0])
            sizes, ips = zip(*points)
            plt.plot(sizes, ips, marker='o', label=library)

        plt.title(f"Benchmark: {result_name}")
        plt.xlabel("Threads")
        plt.ylabel(y_label.replace("_", " ").title())
        plt.xscale('log', base=2)

        all_threads = [size for points in grouped_data.values() for size, _ in points]
        min_size = min(all_threads)
        max_size = max(all_threads)
        min_exp = int(np.floor(np.log2(min_size)))
        max_exp = int(np.ceil(np.log2(max_size)))
        ticks = 2 ** np.arange(min_exp, max_exp + 1)
        plt.xticks(ticks)

        plt.legend()
        plt.grid(True, which="both", ls="--")
        plt.tight_layout()
        plt.savefig(f"plots/{result_name}_{y_label}_results.png", dpi=300)

plot_data("items_per_second")
