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
        print(f"Loading {filepath}")
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
                # {'bm_name': 'AllocationThroughput', 'implementation': 'system', 'size': 8192, 'name': 'BM_MallocFree_Multithreaded/8192/threads:8', 'family_index': 0, 'per_family_instance_index': 15, 'run_name': 'BM_MallocFree_Multithreaded/8192/threads:8', 'run_type': 'iteration', 'repetitions': 1, 'repetition_index': 0, 'threads': 8, 'iterations': 5712, 'real_time': 137789.86525395754, 'cpu_time': 137266.98179271698, 'time_unit': 'ns', 'items_per_second': 7285073.124941815}
                benchmarks.append(enriched_benchmark)

def plot_data(plot_title, series_grouping, x_label, y_label, facet_group=None, plot_filter=None, marker="o", xscale="log"):
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
    axes = axes.flatten()

    for idx, (facet_val, facet_entries) in enumerate(facet_data.items()):
        ax = axes[idx]
        grouped_data = defaultdict(list)
        for entry in facet_entries:
            if y_label in entry:
                grouped_data[entry[series_grouping]].append((entry[x_label], entry[y_label]))

        for grouping_label, data_points in grouped_data.items():
            data_points.sort(key=lambda x: x[0])
            xs, ys = zip(*data_points)
            if series_grouping == "threads":
                grouping_suffix = " threads"
            else:
                grouping_suffix = ""
            ax.plot(xs, ys, marker=marker, label=f"{grouping_label}{grouping_suffix}")

        if facet_group:
            if facet_group == "size":
                # format in B, KB, MB
                facet_val_formatted = f"{facet_val / 1024} KB" if facet_val >= 1024 else f"{facet_val} B"
            else:
                facet_val_formatted = facet_val
            ax.set_title(f"{facet_group}: {facet_val_formatted}")
        else:
            ax.set_title(plot_title.replace("_", " ").title())

        ax.set_xlabel(x_label.title())
        y_label_final = y_label.replace("_", " ").title()
        if y_label == "real_time":
            y_label_final = "Latency"
        if "time" in y_label:
            y_label_final = f"{y_label_final} ({bm['time_unit']})"
        if y_label == "items_per_second":
            y_label_final = "Throughput"
        ax.set_ylabel(y_label_final)
        if xscale == "log":
            ax.set_xscale('log', base=2)

        all_grouped_values = [size for points in grouped_data.values() for size, _ in points]
        if all_grouped_values and xscale == "log":
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
    plt.savefig(f"plots/{plot_title}_{series_grouping}_{x_label}_{y_label}_results.png", dpi=300)
    plt.close()


plot_data("allocation_throughput", "implementation", "threads", "items_per_second", facet_group="size", plot_filter=lambda b: b["bm_name"] == "AllocationThroughput")
plot_data("allocation_throughput", "implementation", "size", "items_per_second", facet_group="threads", plot_filter=lambda b: b["bm_name"] == "AllocationThroughput")
plot_data("allocation_throughput_jemalloc", "threads", "size", "items_per_second", plot_filter=lambda b: b["implementation"] == "jemalloc" and b["bm_name"] == "AllocationThroughput")

plot_data("allocation_latency", "implementation", "threads", "real_time", facet_group="size", plot_filter=lambda b: b["bm_name"] == "AllocationLatency")
plot_data("allocation_latency", "implementation", "size", "real_time", facet_group="threads", plot_filter=lambda b: b["bm_name"] == "AllocationLatency")
plot_data("allocation_latency_jemalloc", "threads", "size", "real_time", plot_filter=lambda b: b["implementation"] == "jemalloc" and b["bm_name"] == "AllocationLatency")

plot_data("allocation_overhead", "implementation", "size", "overhead_bytes", plot_filter=lambda b: b["bm_name"] == "AllocationOverhead", marker=None, xscale=None)

def calculate_ratio(benchmark_filter, ratio_label, numerator_filter, denominator_filter):
    filtered_benchmarks = [bench for bench in benchmarks if all(bench[key] == value for key, value in benchmark_filter.items())]
    numerator_filter_lambda = lambda b: all(b[key] == value for key, value in numerator_filter.items())
    numerator = [bench for bench in filtered_benchmarks if numerator_filter_lambda(bench)]
    denominator_filter_lambda = lambda b: all(b[key] == value for key, value in denominator_filter.items())
    denominator = [bench for bench in filtered_benchmarks if denominator_filter_lambda(bench)]
    if len(numerator) != len(denominator) or len(numerator) != 1:
        print(f"Warning: different number of numerator and denominator benchmarks for {benchmark_filter}")
        return
    print(f"Ratio for {benchmark_filter} {numerator_filter} / {denominator_filter}: {numerator[0][ratio_label] / denominator[0][ratio_label]} {ratio_label}/{ratio_label}")


calculate_ratio(
    {"threads": 8, "size": 2**10},
    "items_per_second",
    {"implementation": "tcmalloc", "bm_name": "AllocationThroughput"},
    {"implementation": "libmalloc", "bm_name": "AllocationThroughput"}
)
calculate_ratio(
    {"threads": 8, "size": 2**20},
    "items_per_second",
    {"implementation": "tcmalloc", "bm_name": "AllocationThroughput"},
    {"implementation": "libmalloc", "bm_name": "AllocationThroughput"}
)
calculate_ratio(
    {"threads": 8, "size": 2**10},
    "real_time",
    {"implementation": "tcmalloc", "bm_name": "AllocationLatency"},
    {"implementation": "libmalloc", "bm_name": "AllocationLatency"}
)
calculate_ratio(
    {"threads": 8, "size": 2**20},
    "real_time",
    {"implementation": "tcmalloc", "bm_name": "AllocationLatency"},
    {"implementation": "libmalloc", "bm_name": "AllocationLatency"}
)

