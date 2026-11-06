# Spreadsheet Error Taxonomy and Benchmark Specification
Examples will be assuming there is a small income statement with years in columns B:D (FY2022 to FY2024) and line items in rows. e.g.
| Row | Line Item | FY2022 (B) | FY2023 (C) | FY2024 (D) |
|---|---|---:|---:|---:|
| 5 | Revenue | 50,000 | 55,000 | 62,000 |
| 6 | COGS | (20,000) | (22,000) | (24,000) |
| 7 | Gross Profit | 30,000 | 33,000 | 38,000 |
| 8 | SG&A | (8,000) | (9,000) | (10,000) |
| 9 | R&D | (3,000) | (3,500) | (4,000) |
| 10 | Operating Expenses | (11,000) | (12,500) | (14,000) |
| 11 | Operating Income | 19,000 | 20,500 | 24,000 |
| 12 | Depreciation | 2,000 | 2,200 | 2,500 |
| 13 | Interest Expense | (1,000) | (1,200) | (1,500) |
| 14 | Pre-Tax Income | 18,000 | 19,300 | 22,500 |
| 15 | Tax Expense (21%) | (3,780) | (4,053) | (4,725) |
| 16 | Net Income | 14,220 | 15,247 | 17,775 |
| 17 | Revenue Growth | — | 10.0% | 12.7% |
| 18 | Operating Margin | 38.0% | 37.3% | 38.7% |

## Error Categories

### 1. Wrong cell reference (`wrong_reference`)
When a formula points at a valid but incorrect cell, often an adjacent row or a similar line item.
- Example 1 (gross profit = Revenue B5 - COGS B6)
  - Correct: `=B5-B6`
  - Incorrect: `=B5-B7` (subtracts Operating Expenses instead of COGS)
- Example 2 (operating margin = Operating Income C12 / Revenue C5)
  - Correct: `=C12/C5`
  - Incorrect: `=C12/C6` (divides by COGS, not Revenue)

### 2. Wrong operator (`wrong_operator`)
When an arithmetic or comparison operator is swapped for another.
- Example 1 (total costs = Salaries + Rent)
  - Correct: `=B8+B9`
  - Incorrect: `=B8-B9`
- Example 2 (flag when actual meets or exceeds budget)
  - Correct: `=IF(C20>=C21,"Over","OK")`
  - Incorrect: `=IF(C20<=C21,"Over","OK")`

### 3. Hardcoded value replacing a formula (`hardcoded_value`)
When a formula cell is overwritten with a constant, so it no longer updates when inputs change. A partial hardcode (a constant folded into the formula) also counts.
- Example 1 (total revenue)
  - Correct: `=SUM(B5:B10)`
  - Incorrect: `=48250`
- Example 2 (tax at 21% of pre-tax income)
  - Correct: `=B14*0.21`
  - Incorrect: `=B14*0.21+1500` (plug amount embedded)

### 4. Wrong year / column (`wrong_period`)
When the formula uses the correct row but the wrong period column, or mixes periods.
- Example 1 (FY2024 revenue growth vs. FY2023)
  - Correct: `=D5/C5-1`
  - Incorrect: `=D5/B5-1` (compares against FY2022)
- Example 2 (FY2024 net income + FY2024 depreciation)
  - Correct: `=D12+D13`
  - Incorrect: `=D12+C13` (mixes in FY2023 depreciation)

### 5. Missing term (`missing_term`)
When one component of a sum or composite calculation is left out.
- Example 1 (operating income = Revenue - COGS - SG&A - R&D)
  - Correct: `=B5-B6-B7-B8`
  - Incorrect: `=B5-B6-B7` (R&D omitted)
- Example 2 (current assets = Cash + Receivables + Inventory)
  - Correct: `=B20+B21+B22`
  - Incorrect: `=B20+B21` (Inventory omitted)

#### 6. Wrong range (`wrong_range`)
When an aggregate covers too few or too many cells.
- Example 1 (sum of six revenue lines)
  - Correct: `=SUM(B5:B10)`
  - Incorrect: `=SUM(B5:B9)`
- Example 2 (sum of line items above a subtotal in B10)
  - Correct: `=SUM(B5:B9)`
  - Incorrect: `=SUM(B5:B10)` (includes the subtotal, double counting)

#### 7. Absolute / relative reference error (`anchoring_error`)
When a `$` anchor is missing or misplaced, so the formula breaks when filled across or down.
- Example 1 (each row times a tax-rate input in F2)
  - Correct: `=B5*$F$2`
  - Incorrect: `=B5*F2`
- Example 2 (sensitivity table)
  - Correct: `=B$4*$A6`
  - Incorrect: `=B4*A6`

#### 8. Wrong function (`wrong_function`)
When a function is replaced with a plausible but incorrect one.
- Example 1 (annual total from 12 monthly values)
  - Correct: `=SUM(B5:B16)`
  - Incorrect: `=AVERAGE(B5:B16)`
- Example 2 (peak monthly value)
  - Correct: `=MAX(B5:B16)`
  - Incorrect: `=MIN(B5:B16)`

#### 9. Unit / scale error (`unit_scale_error`)
When a percentage, thousands, or sign convention is applied incorrectly.
- Example 1 (revenue x growth rate stored as 0.05)
  - Correct: `=B5*C2`
  - Incorrect: `=B5*C2*100`
- Example 2 (convert dollars to $ thousands)
  - Correct: `=B5/1000`
  - Incorrect: `=B5/100`