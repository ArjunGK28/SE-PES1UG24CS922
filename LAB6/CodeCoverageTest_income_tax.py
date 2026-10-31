import pytest
from income_tax import taxable_income, tax_due, refund_status


# ---------- taxable_income ----------

def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000


def test_negative_gross_raises():
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)


def test_old_regime_investments_capped():
    # investments above 150000 are capped, deduction = 50000 + 150000
    assert taxable_income(1000000, "old", 200000) == 800000


def test_unknown_regime_raises():
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "flat", 0)


def test_taxable_floors_at_zero():
    # gross smaller than the deduction -> taxable income is 0
    assert taxable_income(50000, "new", 0) == 0


# ---------- tax_due ----------

def test_below_exemption():
    assert tax_due(200000, 30) == 0


def test_negative_taxable_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-100, 30)


def test_super_senior_lower_slab():
    # age 85 -> exempt 500000, slab = 100000, tax = 5%
    assert tax_due(600000, 85) == 5000


def test_senior_upper_slab():
    # age 65 -> exempt 300000, slab = 400000, tax = 12500 + 20% of 150000
    assert tax_due(700000, 65) == 42500


# ---------- refund_status ----------

def test_refund_on_time():
    assert refund_status(50000, 40000, True) == "refund"


def test_refund_delayed():
    assert refund_status(50000, 40000, False) == "refund delayed"


def test_pay_balance_on_time():
    assert refund_status(30000, 40000, True) == "pay balance"


def test_pay_balance_with_penalty():
    assert refund_status(30000, 40000, False) == "pay balance with penalty"


def test_settled():
    assert refund_status(40000, 40000, True) == "settled"
