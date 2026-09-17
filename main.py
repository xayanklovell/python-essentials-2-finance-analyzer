"""Main menu for the Personal Finance Transaction Analyzer."""

from pathlib import Path

from analytics import running_balance
from parser import STATEMENT_FILE, generate_sample_file, load_transactions


MENU = """===== FINANCE TRANSACTION ANALYZER =====
1. Generate a messy sample statement file
2. Load & validate transactions (reject bad rows)
3. Show running balance (ledger)
4. Category breakdown (income vs expense by tag)
5. Detect duplicate transactions
6. Flag unusual transactions (statistical outliers)
7. Monthly summary report -> file
8. Run self-tests (tests.py)
9. Exit"""

# Replace these messages with function calls as each module is implemented.
PENDING_MESSAGES = {
    4: "Not implemented yet: calculate category totals in analytics.py.",
    5: "Not implemented yet: detect duplicate transactions in analytics.py.",
    6: "Not implemented yet: flag unusual transactions in analytics.py.",
    7: "Not implemented yet: write the monthly summary in reporting.py.",
    8: "Tests are available: run python tests.py. This menu connection is still pending.",
}


def main():
    """Keep showing the menu until the user exits."""
    transactions = []
    rejections = []
    while True:
        print(f"\n{MENU}")
        try:
            choice = int(input("Choose an option (1-9): "))
        except ValueError:
            print("Please enter a whole number from 1 to 9.")
            continue
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not 1 <= choice <= 9:
            print("Please choose a number from 1 to 9.")
            continue

        if choice == 9:
            print("Goodbye!")
            break

        try:
            if choice == 1:
                path = generate_sample_file()
                transactions, rejections = [], []
                print(f"Generated fictional sample statement: {path}")
                print("This replaces the previous sample statement.")
                print("Choose option 2 to load it.")
            elif choice == 2:
                answer = input(f"Statement path [Enter for {STATEMENT_FILE}]: ").strip()
                path = Path(answer).expanduser() if answer else STATEMENT_FILE
                transactions, rejections = load_transactions(path)
                rejected_rows = sum(reason.startswith("row ") for reason in rejections)
                print(f"Loaded {len(transactions)} transactions; rejected {rejected_rows} rows.")
                for reason in rejections:
                    print(f"  {reason}")
                print("Duplicates and sign/category mismatches are kept for later analysis.")
            elif choice == 3:
                if not transactions:
                    print("No valid transactions loaded. Use option 2 first.")
                    continue
                answer = input("Opening balance [Enter for 0]: ").strip()
                start = float(answer) if answer else 0.0
                print("\nLedger in statement order (duplicates included):")
                balances = running_balance(transactions, start)
                for transaction, balance in zip(transactions, balances):
                    print(f"{transaction.formatted()} | balance {balance:+.2f}")
            else:
                print(PENDING_MESSAGES[choice])
        except (OSError, UnicodeError) as error:
            print(f"Could not complete the file operation: {error}")
        except (ValueError, RuntimeError, OverflowError) as error:
            print(f"Could not complete this option: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
