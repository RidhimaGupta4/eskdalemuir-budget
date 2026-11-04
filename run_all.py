"""Reproduce every number and figure in the article: python run_all.py"""
import subprocess, sys, pathlib
here = pathlib.Path(__file__).resolve().parent / "scripts"
for s in ["01_reproduce_algorithm.py", "02_concentration.py", "03_model_vs_measured.py",
          "04_caution_ledger.py", "05_article_numbers.py", "06_figures.py", "07_build_dashboard.py"]:
    print(f"\n=== {s}", flush=True)
    subprocess.run([sys.executable, s], cwd=here, check=True)
print("\nDone. Results in outputs/, figures in outputs/figures/, dashboard in docs/index.html.")
