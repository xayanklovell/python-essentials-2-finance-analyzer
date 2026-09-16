# Personal Finance Transaction Analyzer

Python Essentials 2 advanced challenge by Xayan Kyle Lovell.

## Current progress

The project skeleton is in place. The menu, transaction classes, parser,
analytics, reports, and assertion tests will be built step by step.

## Run locally

Use Python 3.10 or newer. No external packages are required.

```bash
python main.py
python tests.py
```

Use `python3` if that is the Python command on your computer. At this stage,
`main.py` prints a setup message and `tests.py` states that tests are pending.

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
