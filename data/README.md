# Data provenance

All values were extracted from public documents. The documents themselves are not redistributed;
download them from the links below. `source_checksums.txt` lists the SHA-256 of each file used.

| File | Content | Source |
|---|---|---|
| `annex14_table5.csv` | 112 built and consented farms: turbines, MW, average distance, hub height, rotor diameter, amplitude, cumulative amplitude (worst-case scenario). `algorithm_2014` marks the six farms the table footnotes as calculated with the 2014 algorithm; footnote numbers are kept in `footnote`. | Annex 14, "The 2026 Algorithm", Table 5 (DESNZ consultation, 07/07/2026) |
| `annex14_table6.csv` | Same farms, known-case scenario. | Annex 14, Table 6 |
| `latt_coefficients_table7.csv` | Spectral coefficients of the six approved turbine models (12 m/s bin). Checked against both Annex 14 Table 7 and Annex 5 Table 2: 102/102 values identical. | Annex 14 Table 7; Annex 5 (LATT Coefficients Technical Note v5.3, 12/02/2026) |
| `annex13_table3_measured_vs_2014.csv` | Measured impact at the array vs the 2014 budget algorithm, seven farms; which campaign fitted each 2026 model. | Annex 13, AIFCL-101-Phase4-Rev13 (24/11/2023), Table 3; Annex 5, Table 1 |
| `osm_turbines_50km.csv` | Wind turbine positions within 50 km of the array (OSGB36), with the 12 farms used for validation labelled. | OpenStreetMap, Overpass export, November 2026. © OpenStreetMap contributors, ODbL 1.0 |

Other values used in the code, with their sources:
- Budget 0.336 nm: Styles et al. (2005), Keele University report for the MOD, DTI and BWEA.
- Headroom 0.216682 / 0.230316 nm: Annex 15, Headroom and SIL Calculations Explainer (07/07/2026).
- Utilisation re-estimate 82% (amplitude factor √0.82): Xi Engineering (2014), FMB 203 (republished as Annex 12), Section 6.1.

Links:
- Consultation: https://www.gov.uk/government/consultations/eskdalemuir-seismic-array-revised-approach-to-managing-onshore-wind-turbine-interference
- Annexes 4, 5, 7, 11-15: https://www.scottishrenewables.com/membership/policyupdates/policy-making-process/onshore-wind/eskdalemuir-working-group
- Annex 14: https://www.scottishrenewables.com/assets/000/005/634/Annex_14_-_The_2026_Algorithm_original.pdf
- Annex 13: https://www.scottishrenewables.com/assets/000/005/561/AIFCL-101-Phase4-Rev-v13_%28refined_Phase_4_report%29_original.pdf
- Annex 5: https://www.scottishrenewables.com/assets/000/005/431/LATT_Coefficients_TechNote_v5.3_ISSUE_original.pdf
- 2014 report: https://www.scottishrenewables.com/assets/000/005/559/FMB_203_FINAL_V5_original.pdf
- Styles et al. (2005): https://www.keele.ac.uk/geophysics/appliedseismology/windturbinevibrations/final-report.pdf

Licensing note: the consultation is published under the Open Government Licence v3.0 except where otherwise
stated. Some technical annexes are third-party reports; only short numeric extracts are included here, with
attribution, for verification. Check the terms of each source before any wider reuse.
