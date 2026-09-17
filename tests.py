"""Assertion tests for Transaction and RecurringTransaction."""

from models import RecurringTransaction, Transaction

# TODO: Test parsing, invalid rows, missing files, and date normalisation.
# TODO: Test the ledger, closure, duplicates, and outliers.
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

    assert income.formatted() == "2026-08-01 Salary +1500.00 INCOME", "Income display needs a plus sign and two decimal places"
    assert expense.formatted() == "2026-08-02 Groceries -450.50 FOOD", "Expense display must preserve the minus sign and cents"
    assert zero.formatted() == "2026-08-03 No movement +0.00 OTHER", "Zero must display with two decimal places"
    assert str(income) == income.formatted(), "Printing a transaction must use its formatted display"
    assert str(expense) == expense.formatted(), "Expense __str__ must match formatted()"
    assert expense.amount == -450.5, "Formatting must not change the stored amount"
    assert Transaction.total_transactions == starting_count + 3, "Formatting must not create extra transactions"

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

    recurring = RecurringTransaction("2026-08-01", "Rent", -8000, "RENT")
    weekly_income = RecurringTransaction("2026-08-02", "Tutoring", 250, "INCOME", " Weekly ")
    assert isinstance(recurring, Transaction), "RecurringTransaction must inherit Transaction"
    assert recurring.interval == "monthly", "The default interval must be monthly"
    assert weekly_income.interval == "weekly", "Custom intervals must be stripped and lowercase"
    assert recurring.amount == -8000.0, "The subclass must retain the parent's amount handling"
    assert recurring.is_income() is False, "Recurring expenses must inherit the income check"
    assert weekly_income.is_income() is True, "Recurring income must inherit the income check"
    assert recurring.formatted() == "2026-08-01 Rent -8000.00 RENT [recurs monthly]", "The override must extend the parent's display"
    assert str(weekly_income) == "2026-08-02 Tutoring +250.00 INCOME [recurs weekly]", "Inherited __str__ must use the subclass override"
    assert Transaction.total_transactions == starting_count + 5, "Each valid subclass instance must increment the shared count once"
    assert RecurringTransaction.total_transactions == Transaction.total_transactions, "Both classes must share one counter"

    for bad_interval in ("", " ", None, 7):
        try:
            RecurringTransaction("2026-08-01", "Rent", -8000, "RENT", bad_interval)
        except ValueError as error:
            assert str(error), "Invalid intervals need a clear error message"
        else:
            raise AssertionError(f"Invalid interval {bad_interval!r} was accepted")

    try:
        RecurringTransaction("2026-08-01", "Rent", "abc", "RENT")
    except ValueError as error:
        assert str(error), "The subclass must preserve the parent's amount validation"
    else:
        raise AssertionError("The subclass accepted an invalid amount")

    assert Transaction.total_transactions == starting_count + 5, "Invalid subclass instances must not increase the shared count"
    print("All tests passed (transaction models, display, and inheritance).")
