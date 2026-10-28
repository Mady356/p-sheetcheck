# p-SheetCheck

p-SheetCheck is a research project exploring whether spreadsheet formulas can be analyzed like programs to detect semantic errors that Excel itself does not flag.

## Core pipeline

Excel workbook -> formula extraction -> formula representation -> dependency graph -> anomaly detection -> benchmark/evaluation

## Week 2 goal

By the end of Week 2, the team should have the first pieces of an end-to-end pipeline:

1. Load `.xlsx` workbooks and extract formula cells.
2. Represent formulas in a form that can be compared across cells.
3. Build a directed cell-dependency graph.
4. Create a small benchmark of intentionally corrupted spreadsheet formulas.
5. Implement at least one simple anomaly-detection baseline.
6. Run the baseline against the benchmark and report basic results.

See `WEEK_2_ASSIGNMENTS.md` for shared readings and individual responsibilities.

## Repository structure

- `src/` - implementation
- `examples/clean/` - correct example spreadsheets
- `examples/corrupted/` - versions with intentional errors
- `benchmark/` - ground-truth error records and evaluation data
- `tests/` - automated tests
- `research/` - notes, findings, and design decisions

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Working agreement

For Week 2, each person owns one task, but all outputs should be committed to this repository. Keep changes small, document assumptions, and use a separate branch for your assignment before opening a pull request.
