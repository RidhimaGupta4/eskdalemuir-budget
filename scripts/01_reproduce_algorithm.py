"""Section 4/Methods: does the independent implementation reproduce the published 2026 figures?

(a) Whole Table 5: recompute every farm on the 2026 algorithm (worst-case model), keep the six
    legacy farms at their published 2014-algorithm values (as Annex 14 does), compare totals.
(b) 12 farms identified in OpenStreetMap (identified by turbine count and mean distance only;
    amplitudes are never used for matching): farm-average geometry vs per-turbine distances.
(c) Sensitivity to the three choices Annex 14 leaves unstated.
Nothing is fitted: the published values are used only as comparison targets.
"""
import importlib, numpy as np, pandas as pd
from _common import *
import eskdalemuir.algorithm as alg

t5 = table5(); leg = legacy_mask(t5)
mine = np.array([r.amp if leg[i] else worst_case_farm_nm(r.N, r.D, r.H, r.r) for i, r in t5.iterrows()])
c_pub, c_mine = math.sqrt((t5.amp ** 2).sum()), math.sqrt((mine ** 2).sum())
pd.DataFrame({"farm": t5.farm, "legacy_2014_algorithm": leg, "published_nm": t5.amp, "reproduced_nm": mine}).to_csv(OUT / "reproduction_table5.csv", index=False)

o = osm()
rows = []
for farm, g in o[o.validation_farm.notna()].groupby("validation_farm"):
    r = t5[t5.farm == farm].iloc[0]
    per = max(cumulative([amplitude_nm(r.D, r.H, x, k) for x in g.r_km]) for k in LATT)
    avg = worst_case_farm_nm(r.N, r.D, r.H, r.r)
    rows.append(dict(farm=farm, turbines_table=int(r.N), turbines_osm=len(g), mean_r_table=r.r, mean_r_osm=round(g.r_km.mean(), 2),
                     published_nm=r.amp, avg_geometry_nm=avg, per_turbine_nm=per,
                     err_avg=avg / r.amp - 1, err_per_turbine=per / r.amp - 1))
v = pd.DataFrame(rows); v.to_csv(OUT / "validation_12_farms.csv", index=False)
assert (v.turbines_table == v.turbines_osm).all() and (abs(v.mean_r_table - v.mean_r_osm) < 0.05).all()

def median_abs_err(alpha_lo=0.5, alpha_hi=8.0, K=20, integ="trapz"):
    importlib.reload(alg); alg.NCH = K
    fa = np.arange(alpha_lo, alpha_hi + 1e-9, 0.001)
    alg.ALPHA = alg.SNRMAX / np.max(alg._S0(fa) / alg.noise_eka(fa)); alg.FW = alg.F_weight(alg.F)
    e = []
    for farm, g in o[o.validation_farm.notna()].groupby("validation_farm"):
        r = t5[t5.farm == farm].iloc[0]
        a = max(cumulative([alg.amplitude_nm(r.D, r.H, x, k, integ) for x in g.r_km]) for k in alg.LATT)
        e.append(a / r.amp - 1)
    return float(np.median(np.abs(e)))
sens = {"as written (alpha over 0.5-8 Hz, K=20, trapezoid)": median_abs_err(),
        "alpha searched over 0.01-20 Hz": median_abs_err(0.01, 20),
        "K = 10 channels": median_abs_err(K=10), "rectangle rule": median_abs_err(integ="rect")}
importlib.reload(alg)
pd.Series(sens, name="median_abs_error").to_csv(OUT / "sensitivity_open_choices.csv")

summary = dict(C_published=c_pub, C_reproduced=c_mine, C_rel_diff=c_mine / c_pub - 1,
               per_turbine_median_abs_err=float(v.err_per_turbine.abs().median()), per_turbine_max_abs_err=float(v.err_per_turbine.abs().max()),
               avg_median_abs_err=float(v.err_avg.abs().median()), avg_err_min=float(v.err_avg.min()), avg_err_max=float(v.err_avg.max()),
               avg_err_mean=float(v.err_avg.mean()),
               open_choice_max_change=max(sens.values()) - min(sens.values()))
save_json("reproduction_summary.json", summary)
print(pd.Series(summary).round(4).to_string()); print(pd.Series(sens).round(4).to_string())
