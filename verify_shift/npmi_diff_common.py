"""
npmi_diff_signed_boxplot.py 與 npmi_diff_abs_boxplot.py 共用的工具函式。

資料來源：npmi_year_diff.csv（由 npmi_diff.py 產生）
避免兩支畫圖腳本各寫一份幾乎一樣的讀檔／畫圖／統計邏輯，共用部分集中在這裡。
"""

import csv
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 確保中文字（標題、軸標籤）能正常顯示，而不是變成方框
plt.rcParams["font.sans-serif"] = ["PingFang HK", "Heiti TC", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

BASE_DIR = Path(__file__).resolve().parent
INPUT_CSV = BASE_DIR / "npmi_year_diff.csv"

# 色票：references/palette.md 的 sequential blue
COLOR_BOX_FILL = "#2a78d6"
COLOR_BOX_EDGE = "#184f95"
COLOR_MEDIAN = "#0d366b"
COLOR_WHISKER = "#52514e"  # text-secondary
COLOR_TEXT_PRIMARY = "#0b0b0b"
COLOR_TEXT_SECONDARY = "#52514e"
COLOR_GRID = "#e3e2dd"
COLOR_SURFACE = "#fcfcfb"
COLOR_ZERO_LINE = "#e34948"  # red，僅作為 0 的參考線


def load_data():
    """讀取 npmi_year_diff.csv，回傳 (年份區間順序, {年份區間: [npmi_diff, ...]})"""
    diffs_by_interval = defaultdict(list)
    order = []
    with open(INPUT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (int(row["year_from"]), int(row["year_to"]))
            if key not in diffs_by_interval:
                order.append(key)
            diffs_by_interval[key].append(float(row["npmi_diff"]))
    return order, diffs_by_interval


def style_axis(ax):
    ax.set_facecolor(COLOR_SURFACE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(COLOR_GRID)
    ax.yaxis.grid(True, color=COLOR_GRID, linewidth=1, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", colors=COLOR_TEXT_SECONDARY, labelsize=9)


def draw_boxplot(ax, data, labels):
    return ax.boxplot(
        data,
        tick_labels=labels,
        patch_artist=True,
        widths=0.5,
        showfliers=True,
        flierprops=dict(
            marker="o",
            markersize=4,
            markerfacecolor=COLOR_BOX_FILL,
            markeredgecolor=COLOR_SURFACE,
            markeredgewidth=1,
            alpha=0.6,
        ),
        boxprops=dict(facecolor=COLOR_BOX_FILL, edgecolor=COLOR_BOX_EDGE, linewidth=1, alpha=0.55),
        medianprops=dict(color=COLOR_MEDIAN, linewidth=2),
        whiskerprops=dict(color=COLOR_WHISKER, linewidth=1),
        capprops=dict(color=COLOR_WHISKER, linewidth=1),
    )


def make_figure(data, labels, n_per_interval, ylabel, title, output_path, zero_line=False):
    fig, ax = plt.subplots(figsize=(11, 5), facecolor=COLOR_SURFACE)

    draw_boxplot(ax, data, labels)
    if zero_line:
        ax.axhline(0, color=COLOR_ZERO_LINE, linewidth=1, linestyle="--", alpha=0.8)
    ax.set_ylabel(ylabel, color=COLOR_TEXT_PRIMARY, fontsize=10)
    ax.set_xlabel("年份區間", color=COLOR_TEXT_PRIMARY, fontsize=10)
    style_axis(ax)

    for i, n in enumerate(n_per_interval, start=1):
        ax.annotate(
            f"n={n}",
            xy=(i, 0),
            xycoords=("data", "axes fraction"),
            xytext=(0, -32),
            textcoords="offset points",
            ha="center",
            va="top",
            fontsize=8,
            color=COLOR_TEXT_SECONDARY,
        )

    fig.suptitle(title, fontsize=13, color=COLOR_TEXT_PRIMARY, fontweight="bold")
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor=COLOR_SURFACE)
    plt.close(fig)
    print(f"已輸出圖檔：{output_path}")


def compute_stats(values, n_bins=20):
    """
    計算敘述統計。

    注意「眾數」：NPMI 差值是連續數值，幾乎不會有兩筆完全相同的浮點數，
    所以嚴格定義下的眾數（出現次數最多的精確值）通常沒有意義
    （每個值都只出現 1 次，或恰好並列）。因此這裡同時回傳兩種東西：
      - mode_exact：嚴格眾數（statistics.multimode），並附上該眾數的出現次數，
        方便你自己判斷是否有意義（次數為 1 就代表沒有真正的眾數）
      - modal_bin：把資料切成 n_bins 個等寬區間後，出現次數最多的區間
        （範圍 + 該區間的資料筆數），這是連續數值常見、比較有意義的「眾數」表示法
    """
    arr = np.asarray(values, dtype=float)
    n = len(arr)

    exact_modes = statistics.multimode(values)
    exact_mode_count = values.count(exact_modes[0])

    counts, bin_edges = np.histogram(arr, bins=n_bins)
    max_count_idx = int(np.argmax(counts))

    return {
        "n": n,
        "mean": float(np.mean(arr)),
        "std": float(np.std(arr, ddof=1)) if n > 1 else 0.0,
        "min": float(np.min(arr)),
        "q1": float(np.percentile(arr, 25)),
        "median": float(np.median(arr)),
        "q3": float(np.percentile(arr, 75)),
        "max": float(np.max(arr)),
        "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
        "mode_exact_values": exact_modes,
        "mode_exact_count": exact_mode_count,
        "modal_bin_range": (float(bin_edges[max_count_idx]), float(bin_edges[max_count_idx + 1])),
        "modal_bin_count": int(counts[max_count_idx]),
    }


def print_stats_table(order, stats_by_interval, title):
    labels = [f"{y1}→{y2}" for y1, y2 in order]
    print(f"\n=== {title} ===")
    header = (
        f"{'年份區間':<12}{'n':>5}{'平均值':>10}{'標準差':>10}"
        f"{'最小值':>10}{'Q1':>10}{'中位數':>10}{'Q3':>10}{'最大值':>10}{'IQR':>10}"
    )
    print(header)
    for key, label in zip(order, labels):
        s = stats_by_interval[key]
        print(
            f"{label:<12}{s['n']:>5}{s['mean']:>10.4f}{s['std']:>10.4f}"
            f"{s['min']:>10.4f}{s['q1']:>10.4f}{s['median']:>10.4f}"
            f"{s['q3']:>10.4f}{s['max']:>10.4f}{s['iqr']:>10.4f}"
        )

    print(
        "\n眾數（連續數值下嚴格眾數通常不具代表性，故一併提供直方圖眾數區間；"
        "「exact count」若為 1 表示每個值只出現過一次，沒有真正的眾數）："
    )
    for key, label in zip(order, labels):
        s = stats_by_interval[key]
        exact_vals = ", ".join(f"{v:.4f}" for v in s["mode_exact_values"][:3])
        if len(s["mode_exact_values"]) > 3:
            exact_vals += f" ...(共 {len(s['mode_exact_values'])} 個並列)"
        lo, hi = s["modal_bin_range"]
        print(
            f"  {label:<10} exact mode = [{exact_vals}] (count={s['mode_exact_count']})"
            f"   |   modal bin = [{lo:.4f}, {hi:.4f}) (count={s['modal_bin_count']})"
        )
