"""Generate sample statements and load valid transactions from messy rows."""

from pathlib import Path


# Anchor generated files to the project, even when launched from another folder.
DATA_DIR = Path(__file__).resolve().parent / "data"
STATEMENT_FILE = DATA_DIR / "statement.txt"


def generate_sample_file(path=STATEMENT_FILE):
    """Replace the sample statement with fictional valid and broken CSV rows."""
    rows = [
        "2026-08-01,Salary,35000,SALARY",
        "2026-08-02,Rent,-8000,RENT",
        " 2026/08/03 , Groceries , -450.50 , food ",
        "2026-08-04,Bus fare,-30,TRANSPORT",
        "2026-08-05,Electricity,-650,UTILITIES",
        "2026-08-06,Missing category,-25",
        "hello world",
        "2026-08-07,Broken amount,abc,FOOD",
        "2026-08-08,Coffee,-45,FOOD",
        "2026-08-08,Coffee,-45,FOOD",
        "2026-08-09,Expense with wrong sign,200,FOOD",
        "2026-08-10,Income with wrong sign,-300,SALARY",
        '2026-08-11,"Lunch, with friends",-180,FOOD',
        "2026-08-12,Movie,-120,ENTERTAINMENT",
        "2026-08-13,Bank interest,15.75,INTEREST",
        "2026-08-14,Unknown amount,NaN,SHOPPING",
        "2026-02-30,Impossible date,-100,FEES",
        "2026-08-16,,-100,SHOPPING",
        "",
        "2026-09-01,Part-time wages,1500,WAGES",
        "2026-09-02,Books,-250,EDUCATION",
        "2026-09-03,Medical visit,-400,HEALTH",
        "2026-09-04,Refund,50,REFUND",
        "2026-09-05,No movement,0,OTHER",
    ]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as statement:
        statement.write("\n".join(rows) + "\n")
    return path


# TODO: load_transactions(path) returns (transactions, rejection_reasons).
# TODO: Strip whitespace, normalise dates, and convert amounts to float.
# TODO: Handle each bad row separately with a useful reason and row number.
# TODO: Handle missing and empty files without crashing.
