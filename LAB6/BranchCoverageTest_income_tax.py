import pytest
from income_tax import taxable_income, tax_due, refund_status


# ---------- taxable_income ----------
# Branches: gross < 0 (T/F), regime new / old / other,
#           investments > 150000 (T/F), taxable < 0 (T/F)

def test_negative_gross_raises():
    with pytest.raises(ValueError, match="invalid income"):
        taxable_income(-1, "new", 0)


def test_zero_gross_is_valid():
    # boundary: gross == 0 is not negative
    assert taxable_income(0, "new", 0) == 0


def test_new_regime():
    assert taxable_income(1000000, "new", 0) == 925000


def test_old_regime_investments_capped():
    # investments > 150000 -> capped at 150000
    assert taxable_income(1000000, "old", 200000) == 800000


def test_old_regime_investments_not_capped():
    # investments <= 150000 -> used as-is (the branch line coverage missed)
    assert taxable_income(1000000, "old", 100000) == 850000


def test_old_regime_investments_at_cap():
    # boundary: exactly 150000 is not capped
    assert taxable_income(1000000, "old", 150000) == 800000


def test_unknown_regime_raises():
    with pytest.raises(ValueError, match="unknown regime"):
        taxable_income(500000, "flat", 0)


def test_taxable_floors_at_zero():
    assert taxable_income(50000, "new", 0) == 0


def test_taxable_exactly_zero():
    # boundary: gross == deduction -> taxable is 0 via the final return
    assert taxable_income(75000, "new", 0) == 0


# ---------- tax_due ----------
# Branches: taxable < 0 (T/F), age >= 80 / >= 60 / else,
#           taxable <= exempt (T/F), slab <= 250000 (T/F)

def test_negative_taxable_raises():
    with pytest.raises(ValueError, match="invalid amount"):
        tax_due(-100, 30)


def test_below_exemption():
    assert tax_due(200000, 30) == 0


def test_at_exemption_limit():
    # boundary: taxable == exempt -> no tax
    assert tax_due(250000, 30) == 0


def test_regular_lower_slab():
    # age 30 -> exempt 250000, slab = 100000, tax = 5%
    assert tax_due(350000, 30) == 5000


def test_regular_upper_slab():
    # age 30 -> slab = 450000, tax = 12500 + 20% of 200000
    assert tax_due(700000, 30) == 52500


def test_slab_exactly_250000():
    # boundary: slab == 250000 stays in the 5% band
    assert tax_due(500000, 30) == 12500


def test_senior_age_boundary():
    # boundary: age 60 -> exempt 300000
    assert tax_due(300000, 60) == 0
    assert tax_due(400000, 60) == 5000


def test_senior_upper_slab():
    assert tax_due(700000, 65) == 42500


def test_super_senior_age_boundary():
    # boundary: age 80 -> exempt 500000
    assert tax_due(500000, 80) == 0
    assert tax_due(600000, 80) == 5000


def test_super_senior_upper_slab():
    # age 85 -> slab = 500000, tax = 12500 + 20% of 250000
    assert tax_due(1000000, 85) == 62500


# ---------- refund_status ----------
# Branches: difference > 0 / < 0 / == 0, filed_on_time (T/F) in each

def test_refund_on_time():
    assert refund_status(50000, 40000, True) == "refund"


def test_refund_delayed():
    assert refund_status(50000, 40000, False) == "refund delayed"


def test_pay_balance_on_time():
    assert refund_status(30000, 40000, True) == "pay balance"


def test_pay_balance_with_penalty():
    assert refund_status(30000, 40000, False) == "pay balance with penalty"


def test_settled_on_time():
    assert refund_status(40000, 40000, True) == "settled"


def test_settled_late():
    # filing date doesn't matter when nothing is owed either way
    assert refund_status(40000, 40000, False) == "settled"
