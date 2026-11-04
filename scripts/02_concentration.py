"""Sections 1 and 5: how concentrated is the used budget by distance? Published Table 5 only."""
from _common import *
t5 = table5().sort_values("r").reset_index(drop=True)
t5["budget_share_cum"] = (t5.amp ** 2).cumsum() / (t5.amp ** 2).sum()
t5["capacity_share_cum"] = t5.MW.cumsum() / t5.MW.sum()
t5[["farm", "r", "MW", "amp", "budget_share_cum", "capacity_share_cum"]].to_csv(OUT / "concentration_by_distance.csv", index=False)
t = table5(); sh = t.amp ** 2 / (t.amp ** 2).sum()
res = {f"within_{d}km_budget": float(sh[t.r < d].sum()) for d in (17, 20)}
res.update({f"within_{d}km_capacity": float(t.MW[t.r < d].sum() / t.MW.sum()) for d in (17, 20)})
res["hopsrig_plus_little_hartfell_budget"] = float(sh[t.farm.str.match("Hopsrig|Little Hartfell")].sum())
res["free_share_published"] = free_share(math.sqrt((t.amp ** 2).sum()))
res["headroom_over_budget_linear"] = 0.216682 / B_NM
save_json("concentration_summary.json", res); print(pd.Series(res).round(4).to_string())
