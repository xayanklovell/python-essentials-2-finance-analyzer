"""Calculations for transactions; no file access or menu input here."""

from decimal import Decimal, localcontext
import math


def _finite_number(value, label):
    """Convert a numeric value without allowing booleans, NaN, or infinity."""
    if isinstance(value, bool):
        raise ValueError(f"{label} must be a finite number, not a boolean")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{label} must be a finite number") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite and within the float range")
    return number


def running_balance(transactions, start=0.0):
    """Yield a balance after each transaction, preserving statement order."""
    balance = Decimal(str(_finite_number(start, "Opening balance")))
    for transaction in transactions:
        amount = _finite_number(transaction.amount, "Transaction amount")
        # Decimal arithmetic avoids drift such as 0.1 + 0.2 - 0.3 != 0.
        # This precision covers the range of finite floats, including tiny values.
        with localcontext() as context:
            context.prec = 1000
            balance += Decimal(str(amount))
        # Leave the local context before yielding, so the caller is unaffected.
        yield _finite_number(balance, "Calculated balance")


# TODO: make_flagger(threshold) returns a closure comparing amount magnitude.
# TODO: find_duplicates(transactions) uses a set of transaction signatures.
# TODO: find_outliers(transactions) uses statistics.mean and statistics.stdev.
# TODO: category_totals(transactions) sums income and expenses by category.
