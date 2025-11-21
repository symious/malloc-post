import json
import os
import re
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

benchmarks = []
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
                benchmarks.append(enriched_benchmark)

def plot_data(plot_title, series_grouping, x_label, y_label, facet_group=None, plot_filter=None):
    print(f"Plotting {plot_title}, series={series_grouping}, x={x_label}, y={y_label}, facet={facet_group}")
    if plot_filter is None:
        filtered_benchmarks = benchmarks.copy()
    else:
        filtered_benchmarks = [bench for bench in benchmarks if plot_filter(bench)]

    print(f"Series: {set([bench[series_grouping] for bench in benchmarks])}")
    if facet_group:
        print(f"Facets: {set([bench[facet_group] for bench in benchmarks])}")

    if not filtered_benchmarks:
        print("No matching benchmarks")
        return

    if facet_group:
        # Group by facet_group first, then by series_grouping within each facet
        facet_data = defaultdict(list)
        for entry in filtered_benchmarks:
            if y_label in entry:
                facet_data[entry[facet_group]].append(entry)
    else:
        facet_data = {"": filtered_benchmarks}  # Single "facet" for regular plot

    n_facets = len(facet_data)
    n_cols = min(3, n_facets)  # Adjust as needed
    n_rows = (n_facets + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(6 * n_cols, 4 * n_rows), squeeze=False)
    fig.suptitle(plot_title.replace("_", " ").title())
    axes = axes.flatten()

    for idx, (facet_val, facet_entries) in enumerate(facet_data.items()):
        ax = axes[idx]
        grouped_data = defaultdict(list)
        for entry in facet_entries:
            if y_label in entry:
                grouped_data[entry[series_grouping]].append((entry[x_label], entry[y_label]))

        for library, points in grouped_data.items():
            points.sort(key=lambda x: x[0])
            xs, ys = zip(*points)
            ax.plot(xs, ys, marker='o', label=library)

        if facet_group:
            ax.set_title(f"{facet_group}: {facet_val}")
        else:
            ax.set_title(plot_title.replace("_", " ").title())

        ax.set_xlabel(x_label.title())
        ax.set_ylabel(y_label.replace("_", " ").title())
        ax.set_xscale('log', base=2)

        all_grouped_values = [size for points in grouped_data.values() for size, _ in points]
        if all_grouped_values:
            min_size = min(all_grouped_values)
            max_size = max(all_grouped_values)
            min_exp = int(np.floor(np.log2(min_size)))
            max_exp = int(np.ceil(np.log2(max_size)))
            ticks = 2 ** np.arange(min_exp, max_exp + 1)
            ax.set_xticks(ticks)

        ax.legend()
        ax.grid(True, which="both", ls="--")

    # Hide unused subplots
    for idx in range(n_facets, len(axes)):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.savefig(f"plots/{plot_title}_{y_label}_results.png", dpi=300)
    plt.close()


plot_data("malloc", "implementation", "threads", "items_per_second", facet_group="size")
