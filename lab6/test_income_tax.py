import pytest
from income_tax import taxable_income, tax_due, refund_status

#Example test cases:
def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000

def test_below_exemption():
    assert tax_due(200000, 30) == 0

#Write the rest of the test cases so that the code is 90- 100% covered.
