def taxable_income(gross, regime, investments):
    if gross < 0:
        raise ValueError("invalid income")
    if regime == "new":
        deduction = 75000
    elif regime == "old":
        if investments > 150000:
            investments = 150000
        deduction = 50000 + investments
    else:
        raise ValueError("unknown regime")
    taxable = gross - deduction
    if taxable < 0:
        return 0
    return taxable


def tax_due(taxable, age):
    if taxable < 0:
        raise ValueError("invalid amount")
    if age >= 80:
        exempt = 500000
    elif age >= 60:
        exempt = 300000
    else:
        exempt = 250000
    if taxable <= exempt:
        return 0
    slab = taxable - exempt
    if slab <= 250000:
        return slab * 5 // 100
    return 12500 + (slab - 250000) * 20 // 100


def refund_status(tax_paid, tax_due_amount, filed_on_time):
    difference = tax_paid - tax_due_amount
    if difference > 0:
        if filed_on_time:
            return "refund"
        return "refund delayed"
    elif difference < 0:
        if filed_on_time:
            return "pay balance"
        return "pay balance with penalty"
    return "settled"
