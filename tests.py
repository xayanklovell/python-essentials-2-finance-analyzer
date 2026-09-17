"""Assertion tests for transaction models, parsing, and implemented analytics."""

from collections import Counter
from decimal import getcontext
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory

from analytics import make_flagger, running_balance
from models import RecurringTransaction, Transaction
from parser import generate_sample_file, load_transactions, parse_row

# TODO: Test duplicates and outliers.
# TODO: Test reports when reporting.py is implemented.

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

    with TemporaryDirectory() as temporary:
        sample_path = Path(temporary) / "nested" / "statement.txt"
        result = generate_sample_file(sample_path)
        assert result == sample_path and sample_path.is_file(), "Generate the sample in the requested directory"
        sample = sample_path.read_text(encoding="utf-8")
        lines = sample.splitlines()
        assert len(lines) >= 12, "The sample must contain at least 12 rows"
        assert any(count > 1 for line, count in Counter(lines).items() if line), "The sample must plant an exact duplicate"
        assert "hello world" in lines, "The sample must include a junk line"
        assert any("/" in line.split(",")[0] for line in lines), "The sample must include a slash-separated date"
        assert any(len(line.split(",")) == 3 for line in lines), "The sample must include missing fields"
        assert any(",abc," in line for line in lines), "The sample must include a nonnumeric amount"
        assert any(field != field.strip() for line in lines for field in line.split(",")), "The sample must include surrounding whitespace"
        assert any(",200,FOOD" in line for line in lines), "Plant a positive expense-category amount"
        assert any(",-300,SALARY" in line for line in lines), "Plant a negative income-category amount"
        sample_path.write_text("Old sample to replace", encoding="utf-8")
        generate_sample_file(sample_path)
        assert sample_path.read_text(encoding="utf-8") == sample, "Regeneration must replace the old sample rather than append"
        loaded_sample, sample_rejections = load_transactions(sample_path)
        assert len(loaded_sample) == 17, "The supplied sample should retain all 17 valid rows"
        assert len(sample_rejections) == 7, "The supplied sample should reject its seven broken rows"

    # Parser contracts: normalise fields, preserve meaning, and reject bad rows.
    parser_start_count = Transaction.total_transactions
    parsed = parse_row('2024/02/29,"  Market, \"\"Corner\"\"  ",-12.50, food ')
    assert parsed.date == "2024-02-29", "Valid leap dates must normalise to ISO"
    assert parsed.description == 'Market, "Corner"', "CSV quotes and commas must survive"
    assert parsed.amount == -12.5 and isinstance(parsed.amount, float), "Keep signed float amounts"
    assert parsed.category == "FOOD", "Normalise category case and whitespace"
    parsed_snapshot = (parsed.date, parsed.description, parsed.amount, parsed.category)
    bad_rows = [
        "", "   ",
        "2026-02-29,Lunch,-20,FOOD",         # Not a leap year.
        "2026-04-31,Lunch,-20,FOOD",         # Invalid day in this month.
        "2026/08-01,Lunch,-20,FOOD",         # Mixed separators.
        "2026-08-01,Lunch,-20",             # Missing category.
        "2026-08-01,Lunch,-20,FOOD,extra",   # Extra field.
        ",Lunch,-20,FOOD",
        "2026-08-01, , -20,FOOD",
        "2026-08-01,Lunch, ,FOOD",
        "2026-08-01,Lunch,-20, ",
        "2026-08-01,Lunch,banana,FOOD",
        "2026-08-01,Lunch,NaN,FOOD",
        "2026-08-01,Lunch,inf,FOOD",
        "2026-08-01,Lunch,-inf,FOOD",
        "2026-08-01,Lunch,1e999,FOOD",
        "2026-08-01,Lu\x00nch,-20,FOOD",
        "2026-08-01,Lu\x1bnch,-20,FOOD",
        "2026-08-01,Lu\tnch,-20,FOOD",
        "2026-08-01,Lunch,-20,FO\tOD",
        '2026-08-01,"Unclosed,-20,FOOD',
    ]
    for bad_row in bad_rows:
        try:
            parse_row(bad_row)
        except ValueError as error:
            assert str(error), "Rejected rows must explain what failed"
        else:
            raise AssertionError(f"Invalid row was accepted: {bad_row!r}")
    assert Transaction.total_transactions == parser_start_count + 1, "Rejected rows must not count"

    with TemporaryDirectory() as temporary_directory:
        fixture_path = Path(temporary_directory) / "mixed.csv"
        valid_rows = [
            "2026/08/01,Salary,1500,income",
            '2026-08-02,"Groceries, weekly",-50,food',
            "2026-08-03,Refund,20,FOOD",       # Keep positive non-INCOME.
            "2026-08-04,Reversal,-10,INCOME",  # Keep negative INCOME.
            "2026-08-05,Gift,0,custom",        # Unknown categories are allowed.
            '2026-08-02,"Groceries, weekly",-50,food',  # Retain duplicates.
        ]
        records = ["", "DaTe,Description,AMOUNT,Category"] + bad_rows + valid_rows
        binary_records = [record.encode("utf-8") for record in records]
        binary_records += [b"2026-08-06,Bad byte \xff,-1,FOOD", b"2026-08-07,Recovery,-2,OTHER"]
        fixture_path.write_bytes(b"\xef\xbb\xbf" + b"\n".join(binary_records) + b"\n")
        before_load = Transaction.total_transactions
        valid, reasons = load_transactions(fixture_path)
        assert len(valid) == 7, "Keep valid rows, including duplicates and sign mismatches"
        expected_rows = [1] + list(range(3, 3 + len(bad_rows))) + [len(records) + 1]
        assert len(reasons) == len(expected_rows), "Return exactly one reason per rejected row"
        for reason, row_number in zip(reasons, expected_rows):
            assert reason.startswith(f"row {row_number}: "), "Keep physical source row numbers"
        assert Transaction.total_transactions == before_load + 7, "Only loaded valid rows count"
        assert valid[0].date == "2026-08-01", "Accept BOM, leading blank, and case-insensitive header"
        assert valid[2].category == "FOOD" and valid[2].amount == 20, "Retain positive expense-category rows"
        assert valid[3].category == "INCOME" and valid[3].amount == -10, "Retain negative INCOME rows"
        assert valid[4].category == "CUSTOM" and valid[4].amount == 0, "Allow unknown categories and zero"
        assert valid[1].formatted() == valid[5].formatted(), "Retain duplicate records unchanged"
        assert valid[-1].description == "Recovery", "Resume after malformed CSV and invalid UTF-8"
        assert (parsed.date, parsed.description, parsed.amount, parsed.category) == parsed_snapshot, "Loading must not mutate earlier objects"

        fixture_path.write_text("2026-08-08,Café,-3,FOOD\n", encoding="utf-8")
        no_header, reasons = load_transactions(fixture_path)
        assert len(no_header) == 1 and not reasons, "Headers are optional and Unicode text is valid"
        assert no_header[0].description == "Café", "Preserve valid UTF-8 text"
        for payload in (b"", b"date,description,amount,category\n"):
            fixture_path.write_bytes(payload)
            valid, reasons = load_transactions(fixture_path)
            assert not valid and len(reasons) == 1, "Empty and header-only files need one diagnostic"
            assert reasons[0].startswith("file: "), "No-data errors must identify the file"
        for unusable_path in (Path(temporary_directory) / "missing.csv", Path(temporary_directory)):
            valid, reasons = load_transactions(unusable_path)
            assert not valid and len(reasons) == 1, "Missing paths and directories must not crash"
            assert reasons[0].startswith("file: "), "Path errors must identify the file"

    ledger_items = [
        Transaction("2026-08-03", "Income", 100, "INCOME"),
        Transaction("2026-08-01", "Expense", -25, "FOOD"),
        Transaction("2026-08-02", "Refund", 10, "REFUND"),
    ]
    balances = running_balance(ledger_items)
    assert inspect.isgenerator(balances), "The ledger must be a generator"
    original_precision = getcontext().prec
    assert next(balances) == 100.0, "Yield the first balance without consuming the whole ledger"
    assert getcontext().prec == original_precision, "Yielding must not change the caller's decimal context"
    assert list(balances) == [75.0, 85.0], "Keep running state and statement order, not date order"
    assert list(running_balance(ledger_items, start=20)) == [120.0, 95.0, 105.0], "Include the opening balance"
    assert list(running_balance(ledger_items, start=-120)) == [-20.0, -45.0, -35.0], "Allow a negative opening balance"
    assert list(running_balance(iter(ledger_items))) == [100.0, 75.0, 85.0], "Support one-pass transaction iterators"
    assert list(running_balance([], start=20)) == [], "An empty ledger yields no balances"
    assert list(running_balance([ledger_items[1], ledger_items[1]])) == [-25.0, -50.0], "Duplicate transactions remain included"
    assert [item.amount for item in ledger_items] == [100.0, -25.0, 10.0], "The ledger must not change stored amounts"
    pennies = [Transaction("2026-08-01", "Decimal check", amount, "OTHER") for amount in (0.1, 0.2, -0.3)]
    assert list(running_balance(pennies)) == [0.1, 0.3, 0.0], "Decimal amounts must cancel without rounding residue"
    assert all(isinstance(value, float) for value in running_balance(pennies)), "Yield float balances"

    for invalid_start in (float("nan"), float("inf"), -float("inf"), True, "abc"):
        try:
            list(running_balance([], start=invalid_start))
        except ValueError as error:
            assert str(error), "Invalid opening balances need an explanation"
        else:
            raise AssertionError(f"Invalid opening balance accepted: {invalid_start!r}")

    enormous = Transaction("2026-08-01", "Extreme amount", 1e308, "OTHER")
    cent = Transaction("2026-08-01", "One cent", 0.01, "OTHER")
    reversal = Transaction("2026-08-01", "Extreme reversal", -1e308, "OTHER")
    assert list(running_balance([enormous, cent, reversal]))[-1] == 0.01, "Retain small amounts when large values later cancel"
    try:
        list(running_balance([enormous, enormous]))
    except ValueError as error:
        assert "Calculated balance" in str(error), "Explain a balance outside the float range"
    else:
        raise AssertionError("An overflowing balance must not silently become infinity")

    flag = make_flagger(1000)
    large_income = Transaction("2026-08-01", "Large income", 5000, "INCOME")
    large_expense = Transaction("2026-08-01", "Large expense", -5000, "FOOD")
    small = Transaction("2026-08-01", "Small amount", 50, "OTHER")
    assert flag(large_income) is True, "A 5000 income must exceed a 1000 threshold"
    assert flag(large_expense) is True, "A -5000 expense must also exceed the threshold"
    assert flag(small) is False, "A 50 amount must not exceed a 1000 threshold"
    for boundary in (1000, -1000):
        boundary_item = Transaction("2026-08-01", "Boundary", boundary, "OTHER")
        assert flag(boundary_item) is False, "Equality must not trigger a strict threshold"
    lower_flag = make_flagger(10)
    assert lower_flag(small) is True and flag(small) is False, "Each closure must remember its own threshold"
    assert make_flagger(0)(zero) is False, "Zero must not exceed a zero threshold"
    assert make_flagger(0)(large_expense) is True, "A zero threshold must flag nonzero expenses"
    assert make_flagger("1000")(large_income) is True, "Accept numeric input from the menu"
    assert large_expense.amount == -5000.0, "Flagging must not change an expense's sign"

    for invalid_threshold in (-1, float("nan"), float("inf"), -float("inf"), True, None, "abc"):
        try:
            make_flagger(invalid_threshold)
        except ValueError as error:
            assert "Threshold" in str(error), "An invalid threshold needs a clear explanation"
        else:
            raise AssertionError(f"Invalid threshold accepted: {invalid_threshold!r}")

    print("All tests passed (transaction models, parsing, running balances, and threshold flagging).")
