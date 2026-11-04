"""Independent implementation of the Eskdalemuir 2026 algorithm.

Source: "Eskdalemuir Consultation: The 2026 Algorithm" (Annex 14, DESNZ consultation, 07/07/2026),
Section 3, Steps 1-7; constants from Table 2; coefficients from Table 7 (identical to Annex 5, Table 2).
Nothing here is fitted or tuned to published outputs.
"""
import numpy as np

# ---- Table 2 constants (Annex 14) ----
A0, A1, A2 = 0.8678, -8.382, 3.625      # EKA background noise model
FC = 8.0          # FDWF signal corner frequency (Hz)
FCMAX = 6.5       # beam coherency corner frequency (Hz)
FMIN, FMAX = 0.5, 8.0
FNORM = 3.28      # normalisation frequency (Hz)
NCH = 20          # EKA channels in beam coherency model (used as K in B(f))
QC = 100.0        # attenuation parameter (km/s)
RREF = 1.0        # km
SNRMAX = 4.0
TSTAR = 0.15      # s
VREF = 12.0       # m/s
ZL = 0.05         # m
ZREF = 80.0       # m
EKA_E, EKA_N = 326500.0, 604964.0
DF = 0.001        # Hz, frequency step stated for the 2014 algorithm

# ---- Table 7 coefficients (12 m/s bin) ----
LATT = {
    "A_Senvion": dict(CBP=1.10500e-25, p=3.8500, sBP=0.0100,
                      CBM=[6.71310e-27, 3.86520e-27, 3.31510e-27, 8.53820e-27],
                      fj=[2.390, 3.990, 4.800, 5.800], sj=[0.0820, 0.0410, 0.0930, 0.0570],
                      COBN=1.90820e-26, vTIP=71.7712),
    "B_Vestas": dict(CBP=9.33870e-25, p=4.0500, sBP=0.0220,
                     CBM=[1.10960e-26, 4.65310e-27, 3.93720e-27, 1.07170e-29],
                     fj=[2.240, 4.200, 5.900, 7.100], sj=[0.0660, 0.1850, 0.2160, 0.5000],
                     COBN=3.88870e-26, vTIP=69.8),
    "C_Enercon": dict(CBP=2.45010e-26, p=1.3500, sBP=0.0440,
                      CBM=[7.50960e-28, 7.65660e-27, 1.48310e-27, 2.27720e-27],
                      fj=[2.960, 4.600, 5.660, 6.890], sj=[0.0090, 0.0690, 0.1200, 0.0510],
                      COBN=3.40070e-26, vTIP=60.5),
    "D_Nordex": dict(CBP=2.62440e-25, p=3.2175, sBP=0.0319,
                     CBM=[1.25140e-26, 5.39010e-27, 3.52650e-27, 1.04600e-27],
                     fj=[2.140, 4.200, 6.300, 8.000], sj=[0.0210, 0.0700, 0.1045, 0.3380],
                     COBN=3.40070e-26, vTIP=69.9),
    "E_GE": dict(CBP=9.89200e-25, p=3.0360, sBP=0.0100,
                 CBM=[4.23730e-25, 9.86870e-28, 1.67270e-27, 7.89480e-27],
                 fj=[2.680, 4.110, 5.400, 6.700], sj=[0.0100, 0.0320, 0.1360, 0.1120],
                 COBN=1.96920e-26, vTIP=77.49),
    "F_Siemens": dict(CBP=4.16510e-25, p=3.6000, sBP=0.0400,
                      CBM=[2.18000e-26, 1.06550e-26, 7.20380e-29, 7.50130e-28],
                      fj=[2.810, 3.250, 5.300, 6.200], sj=[0.0500, 0.0400, 0.0640, 0.0980],
                      COBN=2.08660e-26, vTIP=77.49),
}

F = np.round(np.arange(FMIN, FMAX + DF / 2, DF), 6)   # frequency grid, inclusive


def noise_eka(f):
    lf = np.log10(f)
    return 10 ** (A0 + A1 * lf + A2 * lf ** 2)


def _S0(f):
    C = np.where(f <= FC, 1.0, (f / FC) ** -2)
    K = NCH
    B = np.where(f < FCMAX, 1 / K + (K - 1) / (2 * K) * (1 + np.cos(np.pi * f / FCMAX)), 1 / K)
    return C ** 2 * np.exp(-2 * np.pi * f * TSTAR) * B


def _alpha():
    # max SNR over the integration band (Annex 14 does not state the search range)
    return SNRMAX / np.max(_S0(F) / noise_eka(F))


ALPHA = _alpha()


def F_weight(f):
    def F0(x):
        S = ALPHA * _S0(x)
        N = noise_eka(x)
        return (S / N) / (S + N)
    return F0(f) / F0(np.array([FNORM]))[0]


FW = F_weight(F)


def P_prop(r_km, f):
    return (RREF / r_km) * np.exp(-2 * np.pi * f * (r_km - RREF) / QC)


def source_psd(D, H, c):
    A = np.pi * (D / 2) ** 2
    vw = VREF * np.log(H / ZL) / np.log(ZREF / ZL)
    fbp = 3 * c["vTIP"] / (np.pi * D)
    scale = A * vw ** 3
    S = c["COBN"] * scale * F ** -2
    for Cj, fj, sj in zip(c["CBM"], c["fj"], c["sj"]):
        S = S + Cj * scale * np.exp(-(F - fj) ** 2 / (2 * sj ** 2))
    kmax = int(np.floor(FMAX / fbp + 1e-12))
    for k in range(1, kmax + 1):
        S = S + c["CBP"] * scale * k ** (-c["p"]) * np.exp(-(F - k * fbp) ** 2 / (2 * c["sBP"] ** 2))
    return S


def amplitude_nm(D, H, r_km, latt, integ="trapz"):
    """rms displacement amplitude at EKA (nm) for one turbine."""
    c = LATT[latt]
    y = source_psd(D, H, c) * FW * P_prop(r_km, F)
    if integ == "trapz":
        I = np.trapezoid(y, F)
    else:  # rectangle rule
        I = np.sum(y) * DF
    return np.sqrt(I) * 1e9


def distance_km(e, n):
    return np.hypot(e - EKA_E, n - EKA_N) / 1000.0


def cumulative(amps):
    return float(np.sqrt(np.sum(np.square(amps))))
