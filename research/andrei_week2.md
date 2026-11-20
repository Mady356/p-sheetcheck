# Week 2: synthetic spreadsheet errors

Implemented `src/mutate.py`, used `openpyxl.load_workbook(data_only=False)`.
The included `examples/clean/sales.xlsx` is "synthetic" monthly business data.
It has such formulas as revenue, variable cost, total cost, and profit for 12 months.

Three provisional category names are used, pending alignment with Ria's taxonomy:

The default run injects 10 errors in distinct cells: 4 reference errors,
3 operator errors, and 3 hardcoded replacements. All other cell values are
preserved. These are just injected errors.

For hardcoded replacements, `corrupted_formula` is `0` without an equals sign.

- The first version works with arithmetic using `+`, `-`, `*`, parentheses,
  numeric literals.
- A reference mutation shifts one column right to another existing
  numeric input.
- A syntactic mutation need not change a numeric answer for every possible
  input. The included fixture was checked to see that all 10 directly mutated
  cells produce different answers for its current inputs.
- openpyxl writes formulas (no calc).

## Verification

Run `python -m unittest discover -s tests -v`. The checks compare every cell
against the CSV, verify the clean file's checksum, repeat the seed, check CSV
appending.