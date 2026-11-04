"""Run with: pytest -q"""
import math, pathlib, sys
import numpy as np, pandas as pd, pytest
from scipy.integrate import simpson
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "src"))
from eskdalemuir import LATT, amplitude_nm, B_NM
D = ROOT / "data"

def test_tables_complete_and_in_order():
    """Running quadrature of each farm amplitude must reproduce the published cumulative column row by row."""
    for name in ("annex14_table5", "annex14_table6"):
        t = pd.read_csv(D / f"{name}.csv")
        assert len(t) == 112
        assert np.max(np.abs(np.sqrt(np.cumsum(t.amp ** 2)) - t.cum)) < 5e-6

def test_published_totals_and_annex15_arithmetic():
    t5, t6 = pd.read_csv(D / "annex14_table5.csv"), pd.read_csv(D / "annex14_table6.csv")
    assert math.isclose(math.sqrt((t5.amp ** 2).sum()), 0.256797, abs_tol=2e-6)
    assert math.isclose(math.sqrt((t6.amp ** 2).sum()), 0.244644, abs_tol=2e-6)
    assert math.isclose(math.sqrt(B_NM ** 2 - 0.256797 ** 2), 0.216682, abs_tol=1e-6)
    assert math.isclose(math.sqrt(B_NM ** 2 - 0.244644 ** 2), 0.230316, abs_tol=1e-6)

def test_legacy_rows_identical_in_both_scenarios():
    t5, t6 = pd.read_csv(D / "annex14_table5.csv"), pd.read_csv(D / "annex14_table6.csv")
    assert t5.algorithm_2014.sum() == 6 and (t5.algorithm_2014 == t6.algorithm_2014).all()
    assert np.allclose(t5.amp[t5.algorithm_2014], t6.amp[t6.algorithm_2014])

def test_coefficient_csv_matches_code():
    c = pd.read_csv(D / "latt_coefficients_table7.csv", float_precision="round_trip").set_index("model")
    same = lambda a, b: math.isclose(a, b, rel_tol=1e-12)
    for k, v in LATT.items():
        assert same(c.loc[k, "CBP"], v["CBP"]) and same(c.loc[k, "p"], v["p"]) and same(c.loc[k, "sigma_BP"], v["sBP"])
        assert same(c.loc[k, "COBN"], v["COBN"]) and same(c.loc[k, "v_tip"], v["vTIP"])
        for j in range(4):
            assert same(c.loc[k, f"CBM{j+1}"], v["CBM"][j]) and same(c.loc[k, f"f{j+1}"], v["fj"][j]) and same(c.loc[k, f"sigma{j+1}"], v["sj"][j])

def _independent(Dm, H, r, t):
    """Second implementation written separately from Annex 14 (Simpson rule, 0.0005 Hz grid)."""
    c = LATT[t]; f = np.linspace(0.5, 8.0, 15001); K = 20
    noise = lambda x: 10 ** (0.8678 - 8.382 * np.log10(x) + 3.625 * np.log10(x) ** 2)
    s0 = lambda x: np.where(x <= 8, 1.0, (x / 8) ** -2) ** 2 * np.exp(-2 * np.pi * x * 0.15) * np.where(x < 6.5, 1 / K + (K - 1) / (2 * K) * (1 + np.cos(np.pi * x / 6.5)), 1 / K)
    alpha = 4 / np.max(s0(f) / noise(f))
    F0 = lambda x: (alpha * s0(x) / noise(x)) / (alpha * s0(x) + noise(x))
    W = F0(f) / F0(np.array([3.28]))[0] * (1 / r) * np.exp(-2 * np.pi * f * (r - 1) / 100)
    sc = math.pi * Dm * Dm / 4 * (12 * math.log(H / 0.05) / math.log(80 / 0.05)) ** 3
    S = c["COBN"] * sc / f ** 2 + sum(a * sc * np.exp(-(f - m) ** 2 / (2 * s * s)) for a, m, s in zip(c["CBM"], c["fj"], c["sj"]))
    fbp, k = 3 * c["vTIP"] / (math.pi * Dm), 1
    while k * fbp <= 8:
        S = S + c["CBP"] * sc * k ** (-c["p"]) * np.exp(-(f - k * fbp) ** 2 / (2 * c["sBP"] ** 2)); k += 1
    return math.sqrt(simpson(S * W, x=f)) * 1e9

@pytest.mark.parametrize("Dm,H,r", [(62, 45, 42.3), (93, 67.9, 19.02), (133, 110, 16.65), (166, 110, 17.38), (5.5, 9, 49.63)])
def test_independent_implementation_agrees(Dm, H, r):
    for t in LATT:
        assert math.isclose(_independent(Dm, H, r, t), amplitude_nm(Dm, H, r, t), rel_tol=1e-6)

def test_annex13_extract():
    a = pd.read_csv(D / "annex13_table3_measured_vs_2014.csv")
    assert len(a) == 7 and a.used_to_fit_2026_model.sum() == 5
    assert not bool(a.loc[a.farm == "Ewe Hill", "used_to_fit_2026_model"].item())

def test_dashboard_built_with_data():
    """docs/index.html must exist, carry its data, and embed the Python reference values it checks itself against."""
    import json, re
    page = (ROOT / "docs" / "index.html").read_text()
    assert "/*__DATA__*/null" not in page
    data = json.loads(re.search(r"const DATA = (\{.*?\});\n</script>", page, re.S).group(1))
    assert len(data["farms"]) == 112 and len(data["engine_tests"]) == 30
    for t in data["engine_tests"]:
        assert math.isclose(t["nm"], amplitude_nm(t["D"], t["H"], t["r"], t["model"]), rel_tol=1e-12)
