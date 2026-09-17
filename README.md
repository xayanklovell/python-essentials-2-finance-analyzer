# Personal Finance Transaction Analyzer

Python Essentials 2 advanced challenge by Xayan Kyle Lovell.

## Current progress

The project skeleton and nine-option menu are in place. The menu handles
invalid input and exits with option 9, Ctrl+C, or end of input.

`Transaction.__init__()` now stores the four transaction fields, cleans surrounding
text whitespace, converts finite amounts to floats, and counts valid objects.
`Transaction.is_income()` returns whether the amount is positive. `formatted()`
and `__str__()` display the date, description, signed amount to two decimal places,
and category. For example: `2026-08-02 Groceries -450.50 FOOD`.
Assertions cover construction, income checks, and display, including invalid
amounts and the zero boundary.

`RecurringTransaction` inherits the transaction fields and income check. Its
constructor uses `super()` and adds an interval (default: `monthly`). Its
`formatted()` override appends the interval to the parent's display, for example
`2026-08-01 Rent -8000.00 RENT [recurs monthly]`. Both classes share one creation
counter. Tests cover inherited methods, custom intervals, and rejected objects.

Option 1 now creates `data/statement.txt` with 24 fictional rows, including
duplicates, missing fields, junk, invalid amounts, wrong signs, and whitespace.
It replaces the previous sample. Generated paths are relative to the project.

Option 2 loads the sample or a custom statement path. The sample produces
17 valid transactions and seven row rejections. Each rejection includes its
physical line number and reason. Missing and empty files produce file diagnostics
instead of crashing; these do not count as rejected rows.

Option 3 shows the running balance after every loaded transaction, using an
optional opening balance (default zero). It preserves statement order and includes
duplicates. Amounts remain floats, while the running sum uses decimal arithmetic
to avoid ordinary decimal rounding drift. Non-finite opening balances and totals
outside the float range produce a clear error.

Option 4 displays income, expenses, and net totals for every category. Income is
positive and expenses are negative, based on the actual amount rather than the
category name. Duplicates remain included, unknown categories are accepted, and
zero-value categories remain visible. Category sums use decimal arithmetic too.

Option 6 now demonstrates the configurable threshold closure. Enter a finite,
nonnegative threshold (default 1000); transactions are flagged only when their
amount magnitude is greater than it. Income and expenses can both be flagged;
amounts equal to the threshold are excluded. Statistical outlier detection is
still pending and is a separate rule from this magnitude check.

Options 5, 7, and 8 explain which work is pending. Duplicate
detection, statistical outliers, reports, and the remaining menu connections will
be built step by step. Run tests directly with `python tests.py`.

## Statement format and cleaning

Each UTF-8 line contains four comma-separated fields:

```text
date,description,amount,category
2026/08/03, Groceries , -450.50 , food
2026-08-04,"Lunch, with friends",-180,FOOD
```

The header is optional on the first nonblank line. The loader strips surrounding
whitespace, converts categories to uppercase, converts amounts to finite floats,
and normalises `YYYY/MM/DD` to `YYYY-MM-DD`. Dates must be real calendar dates.
Quoted commas and doubled quotes are supported; multiline records are rejected.

Blank lines, missing/extra fields, invalid dates or amounts, embedded control
characters, and invalid UTF-8 rows are rejected independently. A UTF-8 byte-order
mark at the start is accepted. Later valid rows still load after a broken row.
Duplicates and sign/category mismatches remain unchanged for later analysis.
Unknown category names are accepted, and file order is preserved.

Custom relative paths are resolved from the terminal's current directory;
the default sample path is always inside this project.

## Run locally

Use Python 3.10 or newer. No external packages are required.

```bash
git clone https://github.com/xayanklovell/python-essentials-2-finance-analyzer.git
cd python-essentials-2-finance-analyzer
python main.py
python tests.py
```

Use `python3` if that is the Python command on your computer. At this stage,
`main.py` opens the menu and `tests.py` runs the current assertions.
A passing result covers transaction models, sample generation, defensive loading,
running balances, threshold flagging, and category totals;
the remaining features and their tests are still to be implemented.

## Project structure

```text
python-essentials-2-finance-analyzer/
|-- main.py          # Menu and user input
|-- models.py        # Transaction class and subclass
|-- parser.py        # Messy sample data and defensive loading
|-- analytics.py     # Ledger, closure, categories, duplicates, outliers
|-- reporting.py     # Monthly report, environment stamp, append-only log
|-- tests.py         # Assertion tests added with each feature
|-- requirements.txt
|-- README.md
|-- .gitignore
|-- data/
    |-- .gitkeep
```

## Build order

1. Set up the repository and skeleton.
2. Add the main menu.
3. Build transaction classes and test their methods.
4. Build the defensive parser and test every broken-input case.
5. Add analytics and tests for their calculations.
6. Add reports and the run log.
7. Connect each menu option to its function and finish the README.
8. Run both Python files from a fresh clone before every push.

Generated statements, reports, and logs belong in `data/` and are excluded
from Git. Only fictional sample transactions should be used in demonstrations.
