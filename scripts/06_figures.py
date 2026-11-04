"""Print-ready versions of the article's four exhibits (PNG 300 dpi, PDF, SVG), drawn from outputs/."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from _common import *

ACCENT, GREY, INK, QUIET, REF, GRID = "#2F6DB5", "#B9B9AF", "#1A1A1A", "#666666", "#8C8C8C", "#E6E6E2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9.5, "axes.edgecolor": QUIET, "axes.labelcolor": QUIET,
                     "xtick.color": QUIET, "ytick.color": QUIET, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none", "pdf.fonttype": 42})
FIG = OUT / "figures"
def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
def titles(fig, title, sub):
    fig.text(0.01, 0.985, title, fontsize=12.5, fontweight="bold", color=INK, va="top")
    fig.text(0.01, 0.925, sub, fontsize=9.5, color=QUIET, va="top")

# ---- Figure 1: what the budget meant (documentary timeline) ----
fig = plt.figure(figsize=(10, 3.5)); ax = fig.add_axes([0, 0, 1, 0.84]); ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.axis("off")
titles(fig, "The limit stayed at 0.336 nm; its stated risk did not", "What the budget meant in each key document, 2005–2026")
eras = [("2005", "Keele report", ["Limit = median of 330", "noisy-day recordings", "20% exceedance", "explicitly accepted"], True),
        ("2014", "New algorithm", ["Re-estimated: about", "0.9 of amplitude", "Set to 1 ‘until, and", "if, further work’"], False),
        ("2020", "Working Group report", ["Called ‘now defunct’", "Set to one ‘for", "simplicity’"], False),
        ("2026", "Consultation", ["Six fitted models,", "all at 12 m/s at once", "No exceedance", "probability stated"], False)]
w, gap, x0 = 22, 3.3, 1
for i, (yr, doc, lines, main) in enumerate(eras):
    x = x0 + i * (w + gap)
    ax.add_patch(FancyBboxPatch((x, 9), w, 29, boxstyle="round,pad=0,rounding_size=1.2", fc=ACCENT if main else "white",
                                alpha=0.13 if main else 1, ec="none"))
    ax.add_patch(FancyBboxPatch((x, 9), w, 29, boxstyle="round,pad=0,rounding_size=1.2", fc="none", ec=ACCENT if main else GREY, lw=2 if main else 1.1))
    ax.text(x + 1.5, 35, yr, fontsize=12, fontweight="bold", color=INK, va="top")
    ax.text(x + 1.5, 30.5, doc, fontsize=9, color=QUIET, va="top")
    for j, l in enumerate(lines): ax.text(x + 1.5, 25.5 - 3.6 * j, l, fontsize=9, color=INK, va="top")
    if i < 3: ax.annotate("", xy=(x + w + gap - 0.3, 31), xytext=(x + w + 0.3, 31), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1))
ax.add_patch(FancyBboxPatch((x0, 1), w, 5.5, boxstyle="round,pad=0,rounding_size=1", fc=ACCENT, alpha=0.13, ec="none"))
ax.text(x0 + w / 2, 3.75, "Risk level stated", ha="center", va="center", fontsize=9, color=INK)
ax.add_patch(FancyBboxPatch((x0 + w + gap, 1), 3 * w + 2 * gap, 5.5, boxstyle="round,pad=0,rounding_size=1", fc="#EFEFEB", ec="none"))
ax.text(x0 + w + gap + (3 * w + 2 * gap) / 2, 3.75, "No exceedance probability stated", ha="center", va="center", fontsize=9, color=INK)
save(fig, "fig1_budget_timeline")

# ---- Figure 2: model / measured, in vs out of sample ----
m = pd.read_csv(OUT / "model_vs_measured.csv")
order = list(m[m.used_to_fit_2026_model].farm) + list(m[~m.used_to_fit_2026_model].farm)
m = m.set_index("farm").loc[order].reset_index()
fig, ax = plt.subplots(figsize=(9, 4.2)); fig.subplots_adjust(top=0.78, left=0.25, right=0.97, bottom=0.14)
titles(fig, f"{int(m.used_to_fit_2026_model.sum())} of {len(m)} checks of the 2026 models use their own fitting data",
       "Predicted ÷ measured impact at the array (Annex 13, Table 3); 1 means the model matches the measurement")
ys = [len(m) - i + (0.35 if fit else 0) for i, fit in enumerate(m.used_to_fit_2026_model)]
for y, r in zip(ys, m.itertuples()):
    ax.plot([r.ratio_2026_published, r.ratio_2014], [y, y], color=GRID, lw=2, zorder=1)
    if not np.isnan(r.ratio_siemens_coeffs):
        ax.plot([r.ratio_siemens_coeffs, r.ratio_2026_published], [y, y], color=ACCENT, alpha=0.35, lw=5, solid_capstyle="round", zorder=2)
        ax.text(r.ratio_siemens_coeffs - 0.02, y, f"{r.ratio_siemens_coeffs:.2f}–{r.ratio_2026_published:.2f}", ha="right", va="center", fontweight="bold", color=INK)
    ax.scatter(r.ratio_2014, y, s=42, facecolor="white", edgecolor=GREY, lw=1.8, zorder=3)
    ax.scatter(r.ratio_2026_published, y, s=42, color=ACCENT, zorder=4)
ax.set_yticks(ys); ax.set_yticklabels([f"{f}   {'in sample' if fit else 'out of sample'}" for f, fit in zip(m.farm, m.used_to_fit_2026_model)])
for lab, fit in zip(ax.get_yticklabels(), m.used_to_fit_2026_model):
    if not fit: lab.set_color(ACCENT); lab.set_fontweight("bold")
ax.axvline(1, color=REF, ls="--", lw=1); ax.text(1.01, max(ys) + 0.55, "Model = measurement", color=QUIET, fontsize=8.5)
ax.set_xlim(0.75, 1.8); ax.set_xlabel("Predicted ÷ measured"); ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.scatter([], [], s=42, facecolor="white", edgecolor=GREY, lw=1.8, label="2014 model"); ax.scatter([], [], s=42, color=ACCENT, label="2026 published figure")
ax.legend(loc="upper right", bbox_to_anchor=(1, 1.2), ncol=2, frameon=False, fontsize=8.5)
fig.text(0.01, 0.01, "Ewe Hill band: published Siemens coefficients applied per turbine (author's calculation) to the published figure. "
         "Harestanes, flagged unreliable in Annex 13, is excluded.", fontsize=7.5, color=QUIET)
save(fig, "fig2_model_vs_measured")

# ---- Figure 3: concentration of the budget by distance ----
c = pd.read_csv(OUT / "concentration_by_distance.csv"); con = load_json("concentration_summary.json")
fig, ax = plt.subplots(figsize=(9, 4.3)); fig.subplots_adjust(top=0.8, left=0.09, right=0.97, bottom=0.13)
titles(fig, f"Farms within 17 km hold {100*con['within_17km_capacity']:.0f}% of capacity but use {100*con['within_17km_budget']:.0f}% of the budget",
       "Built and consented farms in the 2026 consultation (Annex 14, Table 5), cumulative from the nearest outwards; farm-average distances")
x = np.r_[15, c.r.values, 50]
for col, colour, lw, lab in (("capacity_share_cum", GREY, 2, "Share of capacity"), ("budget_share_cum", ACCENT, 2.5, "Share of budget used")):
    ax.step(x, 100 * np.r_[0, c[col].values, 1], where="post", color=colour, lw=lw, label=lab)
ax.axvline(17, color=REF, ls="--", lw=1)
ax.scatter([17, 17], [100 * con["within_17km_budget"], 100 * con["within_17km_capacity"]], color=[ACCENT, GREY], zorder=5, s=25)
ax.text(17.5, 50, f"Within 17 km:\n{100*con['within_17km_budget']:.0f}% of budget used,\n{100*con['within_17km_capacity']:.0f}% of capacity", fontsize=9, color=INK, va="center")
ax.set_xlim(15, 50); ax.set_ylim(0, 103); ax.set_xlabel("Distance from the array (km)"); ax.set_ylabel("Cumulative share (%)")
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True); ax.legend(loc="lower right", frameon=False)
save(fig, "fig3_budget_concentration")

# ---- Figure 4: caution ledger waterfall ----
led = load_json("ledger_summary.json"); cen, lo, hi = led["central"], led["high"], led["low"]
steps = [("As published", 100 * cen["baseline"], "total"), ("Known makers", 100 * cen["shapley_K"], "step"),
         ("Utilisation", 100 * cen["shapley_U"], "step"), ("Legacy farms", 100 * cen["shapley_L"], "step")]
fig, ax = plt.subplots(figsize=(9, 4.3)); fig.subplots_adjust(top=0.8, left=0.07, right=0.97, bottom=0.17)
titles(fig, f"Three caution layers hold {100*(cen['total']-cen['baseline']):.0f} points of budget; over half is legacy allocations",
       "Share of the 0.336 nm budget still free (squared-amplitude terms); each step averaged over all removal orders (Shapley)")
run = 0
for i, (lab, v, kind) in enumerate(steps):
    base = 0 if kind == "total" else run; run = v if kind == "total" else run + v
    ax.bar(i, run - base, bottom=base, width=0.55, color=GREY if kind == "total" else ACCENT)
    ax.text(i, run + 1.5, f"{v:.1f}%" if kind == "total" else f"+{v:.1f}", ha="center", fontweight="bold", color=INK)
    ax.plot([i + 0.275, i + 0.725], [run, run], color=QUIET, lw=0.8, ls=":")
tot = 100 * cen["total"]; i = len(steps)
ax.bar(i, tot, width=0.55, color=GREY); ax.errorbar(i, tot, yerr=[[tot - 100 * lo["total"]], [100 * hi["total"] - tot]], color=INK, capsize=5, lw=1.2)
ax.text(i, 100 * hi["total"] + 7.5, f"{tot:.1f}%", ha="center", fontweight="bold", color=INK)
ax.text(i, 100 * hi["total"] + 2.5, f"range {100*lo['total']:.1f}–{100*hi['total']:.1f}", ha="center", color=QUIET, fontsize=8.5)
ax.axhline(100, color=REF, ls="--", lw=1); ax.text(i + 0.3, 101.5, "Whole budget", ha="right", color=QUIET, fontsize=8.5)
ax.set_xticks(range(len(steps) + 1)); ax.set_xticklabels([s[0] for s in steps] + ["All three removed"])
ax.set_ylim(0, 108); ax.set_yticks([]); ax.spines["left"].set_visible(False); ax.tick_params(axis="x", length=0)
fig.text(0.01, 0.02, "Steps size each layer; none is a recommendation to remove it. Range: legacy-layer reproduction error (−8% to +7%).", fontsize=8, color=QUIET)
save(fig, "fig4_caution_ledger")
print("figures written:", sorted(p.name for p in FIG.iterdir()))
