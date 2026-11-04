"""Open reproduction of the Eskdalemuir seismic budget calculations (2026 algorithm)."""
from .algorithm import LATT, amplitude_nm, cumulative, distance_km, source_psd

B_NM = 0.336  # the budget (threshold), Styles et al. 2005
