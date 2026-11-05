"""Normalize A1 formulas so copied formulas compare equal.

Excel stores a copied formula with different cell letters in every column.
``=C5*C7`` in C9 and ``=D5*D7`` in D9 are the same formula: each one
multiplies the cell four rows up by the cell two rows up, in its own column.

``normalize_formula`` rewrites those references in Excel R1C1 notation,
relative to the cell that contains the formula:

- ``R[-2]C`` is two rows above, same column
- ``RC[1]`` is the same row, one column to the right
- ``RC`` is the formula cell itself
- ``R1C1`` is an absolute reference to A1
- ``R[-4]C1`` and ``R5C[-2]`` are mixed references

Operators, function names, constants, strings, and whitespace are preserved.
Named ranges, table references, and external workbook links are left as
written. This is a first subset for ordinary A1 formulas, not a full Excel
parser.
"""

from __future__ import annotations

import re

from openpyxl.formula.tokenizer import Token, Tokenizer, TokenizerError
from openpyxl.utils.cell import column_index_from_string

# Excel limits. References outside these bounds are left unchanged.
_MAX_COLUMN = 16384  # XFD
_MAX_ROW = 1048576

# A sheet prefix is either Sheet1! or 'My Sheet'!, with '' as an escaped quote.
_SHEET = r"(?:'(?:[^']|'')+'!|[A-Za-z_][\w.]*!)"
_CELL_RE = re.compile(
    rf"^(?P<sheet>{_SHEET})?"
    rf"(?P<col_abs>\$)?(?P<col>[A-Za-z]{{1,3}})"
    rf"(?P<row_abs>\$)?(?P<row>[1-9][0-9]*)$"
)
_COLUMN_RE = re.compile(
    rf"^(?P<sheet>{_SHEET})?(?P<col_abs>\$)?(?P<col>[A-Za-z]{{1,3}})$"
)
_ROW_RE = re.compile(
    rf"^(?P<sheet>{_SHEET})?(?P<row_abs>\$)?(?P<row>[1-9][0-9]*)$"
)


def normalize_formula(formula: str, origin_cell: str) -> str:
    """Return ``formula`` with A1 references rewritten relative to ``origin_cell``.

    ``origin_cell`` is the cell that contains the formula, such as ``"C9"``.
    An optional sheet name (``"Sheet1!C9"``) is accepted and ignored, because
    row and column offsets are measured on that cell's own grid. ``$`` signs
    on the origin are also ignored.

    The result keeps a leading ``=`` when the input has one. A formula that
    cannot be tokenized, or an origin that is not a single cell, raises
    ``ValueError``.
    """
    if not isinstance(formula, str) or formula.strip() == "":
        raise ValueError("formula must be a non-empty string")

    origin_col, origin_row = _parse_origin(origin_cell)
    has_equals = formula.startswith("=")
    source = formula if has_equals else f"={formula}"

    try:
        tokens = Tokenizer(source).items
    except TokenizerError as exc:
        raise ValueError(f"could not parse formula: {formula}") from exc

    parts: list[str] = []
    for token in tokens:
        if token.type == Token.OPERAND and token.subtype == Token.RANGE:
            parts.append(_normalize_reference(token.value, origin_col, origin_row))
        else:
            parts.append(token.value)

    normalized = "".join(parts)
    if has_equals:
        return f"={normalized}"
    return normalized


def _parse_origin(origin_cell: str) -> tuple[int, int]:
    if not isinstance(origin_cell, str):
        raise ValueError("origin_cell must be a cell coordinate such as 'C9'")

    match = _CELL_RE.match(origin_cell.strip())
    if match is None:
        raise ValueError(
            f"origin_cell must be a single A1 cell such as 'C9', got {origin_cell!r}"
        )

    column = _column_number(match.group("col"))
    row = int(match.group("row"))
    if column is None or not 1 <= row <= _MAX_ROW:
        raise ValueError(
            f"origin_cell must be a single A1 cell such as 'C9', got {origin_cell!r}"
        )
    return column, row


def _normalize_reference(reference: str, origin_col: int, origin_row: int) -> str:
    """Rewrite one range token, or return it unchanged if it is not simple A1."""
    if reference.count(":") > 1:
        return reference

    if ":" in reference:
        left_text, right_text = reference.split(":", 1)
        left = _format_endpoint(left_text, origin_col, origin_row, partial=True)
        right = _format_endpoint(right_text, origin_col, origin_row, partial=True)
        if left is None or right is None or left[0] != right[0]:
            return reference
        return f"{left[1]}:{right[1]}"

    endpoint = _format_endpoint(reference, origin_col, origin_row, partial=False)
    if endpoint is None:
        return reference
    return endpoint[1]


def _format_endpoint(
    text: str, origin_col: int, origin_row: int, *, partial: bool
) -> tuple[str, str] | None:
    """Return ``(kind, r1c1)`` for a cell, whole column, or whole row.

    A token with no row number, such as ``AA``, is a name unless it is one
    side of a range like ``A:A``. ``partial`` allows that column or row form.
    """
    cell = _CELL_RE.match(text)
    if cell is not None:
        column = _column_number(cell.group("col"))
        row = int(cell.group("row"))
        if column is None or not 1 <= row <= _MAX_ROW:
            return None
        formatted = _format_row(row, cell.group("row_abs") == "$", origin_row)
        formatted += _format_column(column, cell.group("col_abs") == "$", origin_col)
        return "cell", f"{cell.group('sheet') or ''}{formatted}"

    if not partial:
        return None

    column_ref = _COLUMN_RE.match(text)
    if column_ref is not None:
        column = _column_number(column_ref.group("col"))
        if column is None:
            return None
        formatted = _format_column(
            column, column_ref.group("col_abs") == "$", origin_col
        )
        return "column", f"{column_ref.group('sheet') or ''}{formatted}"

    row_ref = _ROW_RE.match(text)
    if row_ref is not None:
        row = int(row_ref.group("row"))
        if not 1 <= row <= _MAX_ROW:
            return None
        formatted = _format_row(row, row_ref.group("row_abs") == "$", origin_row)
        return "row", f"{row_ref.group('sheet') or ''}{formatted}"

    return None


def _format_row(row: int, absolute: bool, origin_row: int) -> str:
    if absolute:
        return f"R{row}"
    return _format_offset("R", row - origin_row)


def _format_column(column: int, absolute: bool, origin_col: int) -> str:
    if absolute:
        return f"C{column}"
    return _format_offset("C", column - origin_col)


def _format_offset(axis: str, delta: int) -> str:
    if delta == 0:
        return axis
    return f"{axis}[{delta}]"


def _column_number(letters: str) -> int | None:
    try:
        number = column_index_from_string(letters)
    except ValueError:
        return None
    if not 1 <= number <= _MAX_COLUMN:
        return None
    return number
