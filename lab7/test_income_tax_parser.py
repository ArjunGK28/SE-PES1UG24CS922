from hypothesis import given, strategies as st
from income_tax_parser import clean_pan, parse_amount, parse_tax_slab

@given(st.text() | st.none())
def test_clean_pan_no_crash(s):
    try:
        clean_pan(s)
    except Exception as e:
        assert False, f"clean_pan crashed with: {e!r} on input {s!r}"

@given(st.text() | st.none())
def test_parse_amount_no_crash(s):
    try:
        parse_amount(s)
    except Exception as e:
        assert False, f"parse_amount crashed with: {e!r} on input {s!r}"

@given(st.text() | st.none())
def test_parse_tax_slab_no_crash(s):
    try:
        parse_tax_slab(s)
    except Exception as e:
        assert False, f"parse_tax_slab crashed with: {e!r} on input {s!r}"
