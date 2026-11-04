"""Section 4: predicted / measured at the Phase 4 farms (Annex 13, Table 3), in- vs out-of-sample.

Which farms were used to fit each 2026 model comes from Annex 5, Table 1. Only Ewe Hill was not.
For Ewe Hill we also apply the published Siemens coefficients as Annex 14 specifies, per turbine.
"""
from _common import *
a, t6, t5, o = annex13(), table6(), table5(), osm()
pub26 = {"Craig (Carlesgill)": math.hypot(t6.amp[t6.farm.str.startswith("Craig (")].iloc[0], t6.amp[t6.farm.str.startswith("Craig Ext")].iloc[0]),
         "Langhope Rig": t6.amp[t6.farm == "Langhope Rig"].iloc[0], "Clyde": t6.amp[t6.farm == "Clyde"].iloc[0],
         "Ewe Hill": t6.amp[t6.farm == "Ewe Hill"].iloc[0], "Glenkerie": t6.amp[t6.farm == "Middle Hill OR Glenkerie A"].iloc[0],
         "Middle Muir": t6.amp[t6.farm == "Middle Muir WF"].iloc[0]}
a = a[a.farm != "Harestanes"].copy()          # flagged unreliable by Annex 13 itself; reported separately in the text
a["published_2026_nm"] = a.farm.map(pub26)
r = t5[t5.farm == "Ewe Hill"].iloc[0]; g = o[o.validation_farm == "Ewe Hill"]
ewe_siemens = cumulative([amplitude_nm(r.D, r.H, x, "F_Siemens") for x in g.r_km])
a["siemens_coeffs_per_turbine_nm"] = np.where(a.farm == "Ewe Hill", ewe_siemens, np.nan)
a["ratio_2014"] = a.budget_2014_nm / a.measured_nm
a["ratio_2026_published"] = a.published_2026_nm / a.measured_nm
a["ratio_siemens_coeffs"] = a.siemens_coeffs_per_turbine_nm / a.measured_nm
a.to_csv(OUT / "model_vs_measured.csv", index=False)
res = dict(ratio_2014_min=a.ratio_2014.min(), ratio_2014_max=a.ratio_2014.max(),
           ratio_2026_min=a.ratio_2026_published.min(), ratio_2026_max=a.ratio_2026_published.max(),
           ewe_2026_published=float(a.ratio_2026_published[a.farm == "Ewe Hill"].iloc[0]),
           ewe_siemens_coeffs=float(ewe_siemens / 0.0602), harestanes_2014=0.0571 / 0.0662,
           n_in_sample=int(a.used_to_fit_2026_model.sum()), n_farms=len(a))
save_json("model_vs_measured_summary.json", res)
print(a[["farm", "used_to_fit_2026_model", "ratio_2014", "ratio_2026_published", "ratio_siemens_coeffs"]].round(3).to_string(index=False))
