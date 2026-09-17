"""Calculations for transactions; no file access or menu input here."""

from decimal import Decimal, localcontext
import math
import statistics


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


def make_flagger(threshold):
    """Return a function that remembers a nonnegative magnitude threshold."""
    limit = _finite_number(threshold, "Threshold")
    if limit < 0:
        raise ValueError("Threshold must be zero or greater")

    def flag(transaction):
        # Absolute value lets large expenses and large income trigger the rule.
        amount = _finite_number(transaction.amount, "Transaction amount")
        return abs(amount) > limit

    return flag


def category_totals(transactions):
    """Return each category's signed net amount, including every loaded row."""
    totals = {}
    with localcontext() as context:
        context.prec = 1000
        for transaction in transactions:
            amount = Decimal(str(_finite_number(transaction.amount, "Transaction amount")))
            category = transaction.category
            totals[category] = totals.get(category, Decimal(0)) + amount
    return {
        category: _finite_number(total, f"Category total for {category}")
        for category, total in totals.items()
    }


def find_duplicates(transactions):
    """Return every extra occurrence of the same four transaction fields."""
    seen = set()
    duplicates = []
    for transaction in transactions:
        # Use the actual fields: formatted amounts round away small differences.
        signature = (
            transaction.date, transaction.description,
            transaction.amount, transaction.category,
        )
        if signature in seen:
            duplicates.append(transaction)
        else:
            seen.add(signature)
    return duplicates


def find_outliers(transactions):
    """Flag signed amounts more than two sample standard deviations from the mean."""
    items = list(transactions)
    if len(items) < 2:
        return []
    amounts = [_finite_number(item.amount, "Transaction amount") for item in items]
    scale = max(abs(amount) for amount in amounts)
    if scale == 0:
        return []
    # A common scale keeps large finite amounts from overflowing the statistics.
    # It preserves the ratio between distance from the mean and standard deviation.
    scaled_amounts = [amount / scale for amount in amounts]
    average = statistics.mean(scaled_amounts)
    deviation = statistics.stdev(scaled_amounts)
    if deviation == 0:
        return []
    return [
        item for item, amount in zip(items, scaled_amounts)
        if abs(amount - average) > 2 * deviation
    ]
