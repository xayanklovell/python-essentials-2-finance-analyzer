"""Generate sample statements and load valid transactions from messy rows."""

import csv
from datetime import date
from pathlib import Path
import re

from models import Transaction


# Anchor generated files to the project, even when launched from another folder.
DATA_DIR = Path(__file__).resolve().parent / "data"
STATEMENT_FILE = DATA_DIR / "statement.txt"
HEADER = ["date", "description", "amount", "category"]


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


def _read_fields(line):
    """Read exactly four CSV fields from one physical line."""
    line = line.rstrip("\r\n")
    if not line.strip():
        raise ValueError("blank row")
    if any((ord(character) < 32 and character != "\t") or ord(character) == 127
           for character in line):
        raise ValueError("row contains a control character or multiline record")
    try:
        fields = next(csv.reader([line], skipinitialspace=True, strict=True))
    except csv.Error as error:
        raise ValueError(f"malformed CSV: {error}") from error
    if len(fields) != 4:
        raise ValueError(f"expected 4 fields (date, description, amount, category); got {len(fields)}")
    fields = [field.strip() for field in fields]
    for field in fields:
        if any(ord(character) < 32 or ord(character) == 127 for character in field):
            raise ValueError("field contains an embedded control character")
    return fields


def parse_row(line):
    """Return a cleaned transaction, or raise a useful validation error."""
    date_text, description, amount, category = _read_fields(line)
    if not re.fullmatch(r"[0-9]{4}([/-])[0-9]{2}\1[0-9]{2}", date_text):
        raise ValueError("date must use YYYY-MM-DD or YYYY/MM/DD")
    try:
        clean_date = date.fromisoformat(date_text.replace("/", "-")).isoformat()
    except ValueError as error:
        raise ValueError("date is not a real calendar date") from error
    # Date validation happens before construction so rejected rows are not counted.
    # The model validates nonempty fields and converts the amount to a finite float.
    return Transaction(clean_date, description, amount, category)


def load_transactions(path=STATEMENT_FILE):
    """Return (transactions, rejection_reasons), keeping valid rows in file order.

    Row errors start with 'row N:' and file diagnostics start with 'file:'.
    An optional header is accepted on the first nonblank line. Blank lines are
    rejected. Duplicates and sign/category mismatches are kept for later analysis.
    """
    transactions = []
    rejections = []
    saw_bytes = False
    first_record = True
    try:
        # Read and decode each line separately so bad UTF-8 cannot lose later rows.
        with open(path, "rb") as statement:
            for number, raw_line in enumerate(statement, start=1):
                saw_bytes = True
                try:
                    line = raw_line.decode("utf-8-sig" if number == 1 else "utf-8")
                    is_first = first_record
                    if line.strip():
                        first_record = False
                        if is_first and [field.lower() for field in _read_fields(line)] == HEADER:
                            continue
                    transactions.append(parse_row(line))
                except UnicodeDecodeError:
                    first_record = False
                    rejections.append(f"row {number}: invalid UTF-8 text")
                except (ValueError, TypeError, OverflowError) as error:
                    rejections.append(f"row {number}: {error}")
    except (OSError, ValueError, TypeError) as error:
        rejections.append(f"file: could not read {path!s}: {error}")
        return transactions, rejections

    if not saw_bytes:
        rejections.append("file: statement is empty")
    elif not transactions and not rejections:
        rejections.append("file: statement contains a header but no transactions")
    return transactions, rejections
