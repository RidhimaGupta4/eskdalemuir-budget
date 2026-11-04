"""Check every number printed in the article against the outputs of scripts 01-04.

Each entry: (where it appears, the text as printed, computed value, displayed rounding).
The script fails if any computed value does not round to the printed figure.
"""
from _common import *
rep, con = load_json("reproduction_summary.json"), load_json("concentration_summary.json")
mvm, led = load_json("model_vs_measured_summary.json"), load_json("ledger_summary.json")
c, lo, hi = led["central"], led["high"], led["low"]          # 'high' scale = larger 2026 values = smaller layer
checks = [
 ("S1", "41.6% of the budget left", 100 * con["free_share_published"], 41.6, 1),
 ("S1", "sounds like 64%", 100 * con["headroom_over_budget_linear"], 64, 0),
 ("S2", "about 160 tonnes (from 100)", 100 * 2 ** (1 / 1.5), 160, -1),
 ("S2", "about 200 tonnes (the report's own 'c 200'; quoted, checked within 5%)", 100 * 3 ** (1 / 1.5), 200, "quoted"),
 ("S3", "about 0.9 of the amplitude", math.sqrt(0.82), 0.9, 1),
 ("S4", "Harestanes: 2014 model 14% below", 100 * (1 - mvm["harestanes_2014"]), 14, 0),
 ("S4", "2014 over-predicted by 32%", 100 * (mvm["ratio_2014_min"] - 1), 32, 0),
 ("S4", "... to 72%", 100 * (mvm["ratio_2014_max"] - 1), 72, 0),
 ("S4", "2026 figures 17% below", 100 * (1 - mvm["ratio_2026_min"]), 17, 0),
 ("S4", "... to 7% above", 100 * (mvm["ratio_2026_max"] - 1), 7, 0),
 ("S4", "five of the six", mvm["n_in_sample"], 5, 0),
 ("S4", "Ewe Hill published 5% below", 100 * (1 - mvm["ewe_2026_published"]), 5, 0),
 ("S4", "Ewe Hill, Siemens coefficients 10% below", 100 * (1 - mvm["ewe_siemens_coeffs"]), 10, 0),
 ("S5", "about 30 percentage points", 100 * (c["total"] - c["baseline"]), 30, 0),
 ("S5 chart", "within 17 km: 60% of budget", 100 * con["within_17km_budget"], 60, 0),
 ("S5 chart", "within 17 km: 8% of capacity", 100 * con["within_17km_capacity"], 8, 0),
 ("S5", "legacy ratio 1.25", led["legacy_ratio_2014_to_2026_min"], 1.25, 2),
 ("S5", "legacy ratio 1.52", led["legacy_ratio_2014_to_2026_max"], 1.52, 2),
 ("S5", "Hopsrig + Little Hartfell 45%", 100 * con["hopsrig_plus_little_hartfell_budget"], 45, 0),
 ("S5 chart", "baseline 41.6%", 100 * c["baseline"], 41.6, 1),
 ("S5 chart", "+4.9 known makers", 100 * c["shapley_K"], 4.9, 1),
 ("S5 chart", "+8.4 utilisation", 100 * c["shapley_U"], 8.4, 1),
 ("S5 chart", "+16.3 legacy", 100 * c["shapley_L"], 16.3, 1),
 ("S5 chart", "71.2% all three", 100 * c["total"], 71.2, 1),
 ("S5 chart", "range 68.9", 100 * lo["total"], 68.9, 1),
 ("S5 chart", "range 72.8 (72.75 shown as 72.8)", 100 * hi["total"], 72.8, 1),
 ("Methods", "legacy layer 13.7 points", 100 * lo["shapley_L"], 13.7, 1),
 ("Methods", "legacy layer 18.0 points", 100 * hi["shapley_L"], 18.0, 1),
 ("Methods", "8% low", -100 * rep["avg_err_min"], 8, 0),
 ("Methods", "7% high", 100 * rep["avg_err_max"], 7, 0),
 ("Methods", "about 2% low on average", -100 * rep["avg_err_mean"], 2, 0),
 ("Methods", "within 2.5%", -100 * rep["C_rel_diff"], 2.5, 1),
 ("Methods", "0.2505 nm", rep["C_reproduced"], 0.2505, 4),
 ("Methods", "0.2568 nm", rep["C_published"], 0.2568, 4),
 ("Methods", "median error 3.4%", 100 * rep["per_turbine_median_abs_err"], 3.4, 1),
 ("Methods", "largest 7.9%", 100 * rep["per_turbine_max_abs_err"], 7.9, 1),
 ("Methods", "at most 0.3 percentage points", 100 * rep["open_choice_max_change"], 0.3, 1),
]
rows, bad = [], 0
for where, text, val, printed, nd in checks:
    ok = abs(val / printed - 1) <= 0.05 if nd == "quoted" else round(val, nd) == round(printed, nd)
    bad += not ok
    rows.append(dict(section=where, article_text=text, computed=round(val, 4), printed=printed, matches=ok))
t = pd.DataFrame(rows); t.to_csv(OUT / "article_numbers_check.csv", index=False)
print(t.to_string(index=False))
assert bad == 0, f"{bad} article numbers do not match the code"
print(f"\nAll {len(t)} printed numbers match the code.")
