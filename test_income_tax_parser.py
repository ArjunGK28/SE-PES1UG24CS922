from hypothesis import given, strategies as st
from income_tax_parser import clean_pan, parse_amount, parse_tax_slab

@given(st.text() | st.none())
def test_clean_pan_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_parse_amount_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass

@given(st.text() | st.none())
def test_parse_tax_slab_no_crash(s):
    # To-Do: Using try and except complete this function.
    pass
