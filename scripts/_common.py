"""Shared paths and loaders. All inputs are in data/; all results go to outputs/."""
import json, math, pathlib, sys
import numpy as np, pandas as pd
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from eskdalemuir import LATT, amplitude_nm, cumulative, B_NM  # noqa: E402
DATA, OUT = ROOT / "data", ROOT / "outputs"
OUT.mkdir(exist_ok=True); (OUT / "figures").mkdir(exist_ok=True)

def table5():  return pd.read_csv(DATA / "annex14_table5.csv")   # worst-case scenario (published)
def table6():  return pd.read_csv(DATA / "annex14_table6.csv")   # known-case scenario (published)
def annex13(): return pd.read_csv(DATA / "annex13_table3_measured_vs_2014.csv")
def osm():     return pd.read_csv(DATA / "osm_turbines_50km.csv")
def legacy_mask(t): return t.algorithm_2014.values.astype(bool)   # farms the tables assess on the 2014 algorithm

def worst_case_farm_nm(N, D, H, r):
    """Scenario 1 rule: the noisiest of the six approved models, N identical turbines at distance r."""
    return math.sqrt(N) * max(amplitude_nm(D, H, r, k) for k in LATT)

def free_share(c):  return 1 - c * c / (B_NM * B_NM)        # share of B^2 not used
def headroom(c):    return math.sqrt(B_NM * B_NM - c * c)     # Annex 15 definition

def save_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, default=float))
def load_json(name):
    return json.loads((OUT / name).read_text())
