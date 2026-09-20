"""
計算相鄰年份之間，同一個 category pair 的 NPMI 差值。

資料來源：../Downloads/npmi_by_year/npmi_{year}.json（如 CLAUDE.md 所述）
規則：
  - 只比較相鄰年份（2010→2011, 2011→2012, ..., 2019→2020）
  - 若某個 pair 在其中一年沒有出現（代表該年兩個 category 未曾共同出現在足夠資料中），
    則該年份區間跳過此 pair，不計算差值
  - pair 視為無序（category_1/category_2 互換視為同一組），經檢查原始資料在各年間
    排序皆一致，故直接以 (category_1, category_2) 排序後的 tuple 作為 key

輸出：npmi_year_diff.csv，欄位：
  category_1, category_2, year_from, year_to,
  npmi_from, npmi_to, npmi_diff,
  pair_count_from, pair_count_to
"""

import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "Downloads" / "npmi_by_year"
YEARS = list(range(2010, 2021))
OUTPUT_CSV = BASE_DIR / "npmi_year_diff.csv"


def load_year(year: int) -> dict:
    """讀取單一年份的 npmi json，回傳 {pair_key: row}"""
    path = DATA_DIR / f"npmi_{year}.json"
    if not path.exists():
        raise FileNotFoundError(f"找不到檔案：{path}")

    with open(path, encoding="utf-8") as f:
        rows = json.load(f)

    data = {}
    for row in rows:
        key = tuple(sorted((row["category_1"], row["category_2"])))
        if key in data:
            raise ValueError(
                f"{path.name} 內出現重複的 pair {key}，資料可能有問題，請人工確認"
            )
        data[key] = row
    return data


def main():
    year_data = {year: load_year(year) for year in YEARS}

    records = []
    summary = []

    for year_from, year_to in zip(YEARS, YEARS[1:]):
        data_from = year_data[year_from]
        data_to = year_data[year_to]

        common_keys = sorted(set(data_from) & set(data_to)) # 兩年都有的種類
        only_from = set(data_from) - set(data_to) # 如果只有第 t 年有，但是第 t + 1 年沒有的種類
        only_to = set(data_to) - set(data_from)  # 如果只有第 t + 1年沒有，但是第 t 年有的種類

        for key in common_keys:
            row_from = data_from[key]
            row_to = data_to[key]
            records.append(
                {
                    "category_1": key[0],
                    "category_2": key[1],
                    "year_from": year_from,
                    "year_to": year_to,
                    "npmi_from": row_from["NPMI"],
                    "npmi_to": row_to["NPMI"],
                    "npmi_diff": row_to["NPMI"] - row_from["NPMI"],
                    "abs_npmi_diff":abs(row_to["NPMI"] - row_from["NPMI"]),
                    "pair_count_from": row_from["pair_count"],
                    "pair_count_to": row_to["pair_count"],
                }
            )

        summary.append(
            {
                "year_from": year_from,
                "year_to": year_to,
                "n_pairs_from": len(data_from),
                "n_pairs_to": len(data_to),
                "n_common": len(common_keys),
                "n_skipped_only_in_from": len(only_from),
                "n_skipped_only_in_to": len(only_to),
            }
        )


    ### 將結果寫入csv檔案中
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "category_1",
                "category_2",
                "year_from",
                "year_to",
                "npmi_from",
                "npmi_to",
                "npmi_diff",
                "abs_npmi_diff",
                "pair_count_from",
                "pair_count_to",
            ],
        )
        writer.writeheader()
        writer.writerows(records)

    print(f"共輸出 {len(records)} 筆差值紀錄至 {OUTPUT_CSV}\n")
    print(
        f"{'年份區間':<12}{'兩年皆有pair':>12}{'僅前一年有':>12}{'僅後一年有':>12}"
    )
    for s in summary:
        label = f"{s['year_from']}->{s['year_to']}"
        print(
            f"{label:<12}{s['n_common']:>12}"
            f"{s['n_skipped_only_in_from']:>12}{s['n_skipped_only_in_to']:>12}"
        )


if __name__ == "__main__":
    main()
