# tests/

Run with `pytest -q` from the repository root.

`test_core.py` checks that the extracted tables are complete and in order (running quadrature reproduces the published cumulative column row by row), that the published totals and Annex 15 headroom arithmetic hold, that the coefficient file matches the code, that a second, independently written implementation of the algorithm agrees with the main one, and that the dashboard was built with its data.
