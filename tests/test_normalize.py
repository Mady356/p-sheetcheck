"""Examples of A1 formulas and the R1C1 form produced from their origin cell."""

import pytest

from src.normalize import normalize_formula


@pytest.mark.parametrize(
    ("formula", "origin", "expected"),
    [
        # Copied down a product column: same offsets, different letters.
        ("=C5*C7", "C9", "=R[-4]C*R[-2]C"),
        ("=D5*D7", "D9", "=R[-4]C*R[-2]C"),
        ("=E5*E7", "E9", "=R[-4]C*R[-2]C"),
        # Absolute, column-absolute, and row-absolute references.
        ("=$A$1", "D4", "=R1C1"),
        ("=$A5", "C9", "=R[-4]C1"),
        ("=A$5", "C9", "=R5C[-2]"),
        # A range, a mixed absolute multiplier, and a sheet-qualified cell.
        ("=SUM(A1:A10)", "A11", "=SUM(R[-10]C:R[-1]C)"),
        ("=(C5+C6)*$B$1", "C7", "=(R[-2]C+R[-1]C)*R1C2"),
        ("=Sheet2!D10+E10", "C10", "=Sheet2!RC[1]+RC[2]"),
        # Constants and strings stay put; only the reference moves.
        ('=IF(A1>0,"yes","no")', "B2", '=IF(R[-1]C[-1]>0,"yes","no")'),
    ],
)
def test_normalize_formula(formula, origin, expected):
    assert normalize_formula(formula, origin) == expected


def test_copied_formulas_share_one_pattern():
    pattern = normalize_formula("=C5*C7", "C9")
    assert normalize_formula("=D5*D7", "D9") == pattern
    assert normalize_formula("=E5*E7", "E9") == pattern


def test_absolute_reference_does_not_depend_on_origin():
    assert normalize_formula("=$A$1", "C9") == "=R1C1"
    assert normalize_formula("=$A$1", "Z100") == "=R1C1"


def test_quoted_sheet_and_whole_column_ranges():
    assert normalize_formula("='My Sheet'!$B$3", "D9") == "='My Sheet'!R3C2"
    assert normalize_formula("=SUM(A:A)", "C1") == "=SUM(C[-2]:C[-2])"
    assert normalize_formula("=SUM($1:$1)", "C5") == "=SUM(R1:R1)"


def test_named_range_whitespace_and_multi_letter_column_are_preserved():
    assert normalize_formula("=Revenue+C5", "C6") == "=Revenue+R[-1]C"
    # A short name is not a whole-column reference; only A:A is.
    assert normalize_formula("=AA+AA1", "AB2") == "=AA+R[-1]C[-1]"
    assert normalize_formula("=C5 * C7", "C9") == "=R[-4]C * R[-2]C"
    assert normalize_formula("=AA1", "AB2") == "=R[-1]C[-1]"


def test_formula_without_leading_equals():
    assert normalize_formula("C5*C7", "C9") == "R[-4]C*R[-2]C"


def test_invalid_origin_and_unclosed_string_raise():
    with pytest.raises(ValueError):
        normalize_formula("=A1", "not-a-cell")
    with pytest.raises(ValueError):
        normalize_formula('="unterminated', "A1")
