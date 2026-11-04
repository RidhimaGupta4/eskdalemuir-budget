"""Section 5: the caution ledger, in published terms wherever a published figure exists.

baseline  Annex 14 Table 5 (worst case), as published
K         known turbine makers: Annex 14 Table 6 (known case), as published
U         utilisation: the 2014 report's own estimate, amplitude x sqrt(0.82)
L         legacy: the six farms on the 2014 algorithm recalculated on the 2026 worst-case model
          (author's calculation; no published 2026 value exists)
Attribution: Shapley values over {K, U, L} (order-independent; shares sum to the total change).
Uncertainty on L: reproduction errors from script 01 for the method used here (farm-average geometry):
true = mine / (1 + error), error in [min, max] over the 12 validation farms.
"""
import itertools
from _common import *
t5, t6 = table5(), table6(); leg = legacy_mask(t5)
assert len(t5) == len(t6) and (t5[["N", "MW", "r", "H", "D"]].values == t6[["N", "MW", "r", "H", "D"]].values).all()
assert np.allclose(t5.amp[leg], t6.amp[leg]) and leg.sum() == 6
w26 = np.array([worst_case_farm_nm(r.N, r.D, r.H, r.r) for _, r in t5.iterrows()])
rep = load_json("reproduction_summary.json")
scales = {"central": 1.0, "low": 1 / (1 + rep["avg_err_max"]), "high": 1 / (1 + rep["avg_err_min"])}

def C(S, s=1.0):
    a = (t6.amp.values if "K" in S else t5.amp.values).copy()
    if "L" in S: a[leg] = w26[leg] * s
    return math.sqrt(float((a ** 2).sum())) * (math.sqrt(0.82) if "U" in S else 1.0)

def shapley(s):
    P = ["K", "U", "L"]; v = lambda S: free_share(C(set(S), s)); out = {}
    for p in P:
        others = [q for q in P if q != p]
        out[p] = sum(math.factorial(k) * math.factorial(2 - k) / 6 * (v(S + (p,)) - v(S))
                     for k in range(3) for S in itertools.combinations(others, k))
    return out

scen = [dict(layers="+".join(S) or "baseline", C_nm=C(set(S)), headroom_nm=headroom(C(set(S))), free_share=free_share(C(set(S))))
        for k in range(4) for S in itertools.combinations(["K", "U", "L"], k)]
pd.DataFrame(scen).to_csv(OUT / "ledger_scenarios.csv", index=False)
res = {}
for name, s in scales.items():
    sh = shapley(s); tot = free_share(C({"K", "U", "L"}, s))
    assert abs(free_share(C(set())) + sum(sh.values()) - tot) < 1e-12        # Shapley efficiency
    res[name] = dict(scale=s, baseline=free_share(C(set())), **{f"shapley_{k}": v for k, v in sh.items()}, total=tot)
res["legacy_ratio_2014_to_2026_min"] = float((t5.amp[leg] / w26[leg]).min())
res["legacy_ratio_2014_to_2026_max"] = float((t5.amp[leg] / w26[leg]).max())
save_json("ledger_summary.json", res); print(json.dumps(res, indent=1, default=lambda x: round(x, 4)))
