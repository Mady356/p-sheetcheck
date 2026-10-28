# Week 2 Assignments

## Universal readings — everyone

Read these before starting your individual assignment. The goal is not to memorize the documentation; it is to make sure everyone understands the same basic vocabulary.

1. **Microsoft Support — Overview of formulas in Excel**  
   Focus on cell references and the difference between relative, absolute, and mixed references.  
   https://support.microsoft.com/en-us/excel/get-started/overview-of-formulas-in-excel

2. **openpyxl — Tutorial: Loading from a file**  
   Focus on `load_workbook()` and the `data_only` option.  
   https://openpyxl.readthedocs.io/en/3.1/tutorial.html#loading-from-a-file

3. **openpyxl — Parsing Formulas**  
   Read the Tokenizer section and skim formula translation.  
   https://openpyxl.readthedocs.io/en/3.1/formula.html

4. **NetworkX — Tutorial**  
   Read Creating a graph, Nodes, Edges, and Directed graphs.  
   https://networkx.org/documentation/latest/tutorial

Expected shared reading time: about 30-45 minutes.

---

## Andre — Workbook ingestion and formula inventory

### Goal
Create the first reusable function for loading an Excel workbook and identifying every formula cell.

### Tasks
- Use `openpyxl.load_workbook()` to open at least two small `.xlsx` workbooks.
- Iterate through all worksheets and identify cells whose values are formulas.
- Record for each formula cell: sheet name, coordinate, and raw formula string.
- Return the results in a simple Python structure such as a list of dictionaries.
- Add one small test workbook to `examples/clean/`.

### Deliverable
Create `src/extract.py` containing a function such as:

```python
extract_formulas(path) -> list[dict]
```

Also add a short note in `research/andre_week2.md` explaining any edge cases you noticed.

### Helpful notes
- Keep `data_only=False` so that openpyxl returns formulas rather than cached results.
- Start with normal formulas before worrying about macros, external links, or unusual workbook features.

---

## Ria — Spreadsheet error taxonomy and benchmark specification

### Goal
Define exactly what kinds of errors our first benchmark should test.

### Tasks
- Review small financial/business spreadsheets and identify formula mistakes that Excel would still accept.
- Define at least five error categories, for example:
  - wrong cell reference
  - wrong operator
  - hardcoded value replacing a formula
  - reference to the wrong year/column
  - missing term in a formula
- For each category, create two concrete examples showing a correct and incorrect formula.
- Propose a CSV format for recording benchmark ground truth.

### Deliverable
Create:
- `research/error_taxonomy.md`
- `benchmark/errors_template.csv`

The CSV should at minimum contain: workbook, sheet, cell, correct_formula, corrupted_formula, error_type.

### Helpful notes
Focus on errors that are syntactically valid Excel formulas. We are testing semantic mistakes, not formulas Excel already marks as invalid.

---

## Maadhavan — Formula normalization and relative-reference representation

### Goal
Create a representation that lets us recognize when copied formulas have the same structure even though their A1 references differ.

### Tasks
- Start with simple formulas such as `=C5*C7`, `=D5*D7`, and `=E5*E7`.
- Explore using `openpyxl.formula.Tokenizer` to separate operators, constants, functions, and references.
- Design a representation for references relative to the formula cell. For example, a reference two rows above in the same column should look the same regardless of the actual column letter.
- Make sure you think about relative, absolute, and mixed references (`A1`, `$A$1`, `$A1`, `A$1`).
- Implement a first normalization function for simple A1-style formulas.

### Deliverable
Create `src/normalize.py` with a function such as:

```python
normalize_formula(formula, origin_cell)
```

Add 8-10 example formulas and expected normalized outputs in `tests/test_normalize.py`.

### Helpful notes
Do not try to support every Excel function immediately. A well-defined subset with tests is better than a broad but unreliable parser.

---

## Aneesh — Dependency graph construction

### Goal
Represent a workbook as a directed graph where formula dependencies become edges.

### Tasks
- Use formula references to determine which cells each formula depends on.
- Build a `networkx.DiGraph`.
- Represent each cell with a unique node identifier, including its sheet name.
- If `Sheet1!C1 = A1 + B1`, create edges from `A1 -> C1` and `B1 -> C1`.
- Test the graph on at least one clean example workbook.
- Print or export useful graph information such as predecessors and successors for formula cells.

### Deliverable
Create `src/dependency_graph.py` with a function such as:

```python
build_dependency_graph(path)
```

Add one small diagram, adjacency listing, or screenshot to `research/dependency_graph_example.md`.

### Helpful notes
Use a directed graph, not an undirected graph. The direction should represent information flow: referenced cell -> formula cell.

---

## Andrei — Synthetic spreadsheet error generator

### Goal
Automate the process of creating corrupted versions of correct spreadsheets for evaluation.

### Tasks
- Start with one clean spreadsheet in `examples/clean/`.
- Implement at least three mutation types from Ria's taxonomy.
- Examples might include changing one referenced column, replacing `+` with `-`, or replacing a formula with a constant.
- Save corrupted workbooks into `examples/corrupted/` without overwriting the clean version.
- Record each mutation in the benchmark CSV format.

### Deliverable
Create `src/mutate.py` that can produce corrupted workbook copies and append ground-truth records to `benchmark/errors.csv`.

Aim for at least 10 total injected errors across one or more workbooks.

### Helpful notes
Every mutation must be reproducible and recorded. We should always know exactly which cell was changed and what the correct formula was.

---

## Federico — Baseline anomaly detector and evaluation harness

### Goal
Create the first simple detector so we have something to compare future algorithms against.

### Tasks
- Implement a deliberately simple formula-pattern baseline.
- One possible approach: across a row or column of formulas, identify the dominant normalized formula pattern and flag cells that differ.
- Load the benchmark ground truth generated by the team.
- Compare predicted suspicious cells against actual injected errors.
- Calculate at minimum: true positives, false positives, false negatives, precision, and recall.

### Deliverable
Create:
- `src/baseline.py`
- `src/evaluate.py`
- `research/baseline_results.md`

If upstream normalization is not ready yet, use a temporary simplified representation and clearly document it so it can be replaced later.

### Helpful notes
The first baseline is not supposed to be sophisticated. Its purpose is to establish a measurable reference point that later structural/graph methods need to beat.

---

## End-of-week integration milestone

At the next meeting, we should be able to demonstrate as much of this flow as possible:

1. Load an `.xlsx` workbook.
2. Extract its formulas.
3. Normalize at least simple repeated formulas.
4. Construct a dependency graph.
5. Generate intentionally corrupted copies.
6. Run a baseline detector.
7. Compare the detector with known injected errors.

Everyone should come prepared to explain both what worked and what assumptions or edge cases caused problems.
