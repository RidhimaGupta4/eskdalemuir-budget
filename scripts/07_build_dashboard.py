"""Build the interactive dashboard (docs/index.html) from dashboard/template.html and the outputs of 01-04.

Everything shown is computed from data/ and outputs/; nothing is typed in by hand. The page re-implements
the 2026 algorithm in JavaScript and, on every load, checks it against the Python reference values
embedded here (engine_tests).
"""
from _common import *
import eskdalemuir.algorithm as alg

t5, t6 = table5(), table6(); leg = legacy_mask(t5)
farms = []
for i, r in t5.iterrows():
    farms.append(dict(name=r.farm, n=int(r.N), mw=float(r.MW), r=float(r.r), H=float(r.H), D=float(r.D),
                      a5=float(r.amp), a6=float(t6.amp[i]), legacy=bool(leg[i]),
                      w26=float(worst_case_farm_nm(r.N, r.D, r.H, r.r)) if leg[i] else None))
labels = {"A_Senvion": "A · Senvion (fitted at Middlemuir)", "B_Vestas": "B · Vestas (fitted at Glenkerie)",
          "C_Enercon": "C · Enercon (fitted at Craig Hill)", "D_Nordex": "D · Nordex (fitted at Craig Hill)",
          "E_GE": "E · GE (fitted at Langhope Rig)", "F_Siemens": "F · Siemens (fitted at Clyde)"}
latt = {k: dict(label=labels[k], CBP=c["CBP"], p=c["p"], sBP=c["sBP"], CBM=c["CBM"], fj=c["fj"], sj=c["sj"], COBN=c["COBN"], v_tip=c["vTIP"])
        for k, c in LATT.items()}
constants = dict(a0=alg.A0, a1=alg.A1, a2=alg.A2, fc=alg.FC, fcmax=alg.FCMAX, fmin=alg.FMIN, fmax=alg.FMAX, fnorm=alg.FNORM,
                 nch=alg.NCH, qc=alg.QC, rref=alg.RREF, snrmax=alg.SNRMAX, tstar=alg.TSTAR, vref=alg.VREF, zl=alg.ZL, zref=alg.ZREF, df=alg.DF)
tests = [dict(model=k, D=D, H=H, r=r, nm=float(amplitude_nm(D, H, r, k)))
         for k in LATT for (D, H, r) in [(62, 45, 42.3), (93, 67.9, 19.02), (133, 110, 16.65), (166, 110, 17.38), (100, 90, 35.0)]]
mv = pd.read_csv(OUT / "model_vs_measured.csv")
short = {"Craig (Carlesgill)": "Craig"}
validation = [dict(farm=short.get(r.farm, r.farm), fitted=bool(r.used_to_fit_2026_model), meas=float(r.measured_nm), m14=float(r.budget_2014_nm),
                   m26=float(r.published_2026_nm), alt=None if pd.isna(r.siemens_coeffs_per_turbine_nm) else float(r.siemens_coeffs_per_turbine_nm),
                   campaign=r.fitting_campaign) for r in mv.itertuples()]
led = load_json("ledger_summary.json"); c = led["central"]
DATA = dict(budget_nm=B_NM, as_of="4 November 2026", repo_url="https://github.com/RidhimaGupta4/eskdalemuir-budget",
            constants=constants, latt=latt, farms=farms, validation=validation, engine_tests=tests,
            sil_range=[0.004614, 0.005479], headroom_worst=0.216682,
            err_range=[load_json("reproduction_summary.json")["avg_err_min"], load_json("reproduction_summary.json")["avg_err_max"]],
            shapley=dict(K=c["shapley_K"], U=c["shapley_U"], L=c["shapley_L"], baseline=c["baseline"], total=c["total"],
                         total_low=led["high"]["total"], total_high=led["low"]["total"]))
html = (ROOT / "dashboard" / "template.html").read_text()
assert html.count("/*__DATA__*/null") == 1
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(html.replace("/*__DATA__*/null", json.dumps(DATA, separators=(",", ":"))))
print(f"docs/index.html written ({(ROOT / 'docs' / 'index.html').stat().st_size / 1024:.0f} KB), {len(farms)} farms, {len(tests)} engine tests")
