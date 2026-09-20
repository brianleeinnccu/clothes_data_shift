"""
畫出「相鄰年份 |NPMI 差值|」（絕對值）的分布概況（盒鬚圖），並印出敘述統計。

資料來源：npmi_year_diff.csv（由 npmi_diff.py 產生）
橫軸：年份區間（2010->2011, 2011->2012, ..., 2019->2020）
輸出：npmi_year_diff_abs_boxplot.png
"""

from npmi_diff_common import (
    BASE_DIR,
    compute_stats,
    load_data,
    make_figure,
    print_stats_table,
)

OUTPUT_PNG = BASE_DIR / "npmi_year_diff_abs_boxplot.png"


def main():
    order, diffs_by_interval = load_data()
    labels = [f"{y1}→{y2}" for y1, y2 in order]
    abs_diffs_by_interval = {k: [abs(v) for v in diffs_by_interval[k]] for k in order}
    n_per_interval = [len(abs_diffs_by_interval[k]) for k in order]

    make_figure(
        [abs_diffs_by_interval[k] for k in order],
        labels,
        n_per_interval,
        ylabel="|NPMI 差值|",
        title="相鄰年份 |NPMI 差值| 分布概況",
        output_path=OUTPUT_PNG,
        zero_line=False,
    )

    stats_by_interval = {k: compute_stats(abs_diffs_by_interval[k]) for k in order}
    print_stats_table(order, stats_by_interval, "|NPMI 差值|（絕對值）敘述統計")


if __name__ == "__main__":
    main()
