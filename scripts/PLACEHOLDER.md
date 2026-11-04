# scripts/

Run in order, or all at once with `python run_all.py` from the repository root. Each script reads `data/` and writes to `outputs/`.

| Script | Article section | Output |
|---|---|---|
| `01_reproduce_algorithm.py` | Methods, Section 4 | Reproduction of Table 5, 12-farm validation, sensitivity to unstated choices |
| `02_concentration.py` | Sections 1 and 5 | Budget concentration by distance |
| `03_model_vs_measured.py` | Section 4 | Predicted / measured, in-sample vs out-of-sample |
| `04_caution_ledger.py` | Section 5 | Layer scenarios, Shapley shares, uncertainty band |
| `05_article_numbers.py` | All | Checks every number printed in the article; fails on any mismatch |
| `06_figures.py` | All | Print-ready figures (PNG 300 dpi, PDF, SVG) |
| `07_build_dashboard.py` | - | Builds the interactive dashboard, `docs/index.html` |
| `_common.py` | - | Shared paths and loaders |
