"""Assertion tests for the two Transaction methods implemented so far."""

from models import Transaction

# TODO: Test parsing, invalid rows, missing files, and date normalisation.
# TODO: Test formatted display, inheritance, ledger, closure, duplicates, and outliers.
# TODO: Use helpful assertion messages and temporary files for file tests.

if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Assertions are disabled. Run python tests.py without -O.")

    starting_count = Transaction.total_transactions
    income = Transaction("2026-08-01", "Salary", 1500, "INCOME")
    expense = Transaction(" 2026-08-02 ", " Groceries ", "-450.50", " food ")
    zero = Transaction("2026-08-03", "No movement", 0, "OTHER")

    assert income.date == "2026-08-01", "The constructor must store the date"
    assert income.description == "Salary", "The constructor must store the description"
    assert income.amount == 1500.0, "The constructor must retain the amount"
    assert isinstance(income.amount, float), "Integer amounts must become floats"
    assert expense.date == "2026-08-02", "Surrounding date whitespace must be removed"
    assert expense.description == "Groceries", "Description whitespace must be removed"
    assert expense.category == "FOOD", "Categories must be stripped and uppercase"
    assert expense.amount == -450.5, "Numeric text must retain its negative value"
    assert isinstance(expense.amount, float), "Numeric text must become a float"
    assert income.is_income() is True, "A positive amount must be income"
    assert expense.is_income() is False, "A negative amount must not be income"
    assert zero.is_income() is False, "Zero must not count as income"
    assert Transaction.total_transactions == starting_count + 3, "Count every valid object once"

    for bad_amount in ("abc", "NaN", "inf", "-inf", "1e999", True, None):
        try:
            Transaction("2026-08-01", "Invalid amount", bad_amount, "FOOD")
        except ValueError as error:
            assert str(error), "Invalid amounts need a clear error message"
        else:
            raise AssertionError(f"Invalid amount {bad_amount!r} was accepted")

    for date, description, category in ((" ", "Lunch", "FOOD"),
                                        ("2026-08-01", " ", "FOOD"),
                                        ("2026-08-01", "Lunch", " ")):
        try:
            Transaction(date, description, -20, category)
        except ValueError as error:
            assert str(error), "Empty fields need a clear error message"
        else:
            raise AssertionError("An empty transaction field was accepted")

    assert Transaction.total_transactions == starting_count + 3, "Invalid objects must not increase the count"
    print("All tests passed (Transaction construction and income checks only).")
