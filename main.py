"""Main menu for the Personal Finance Transaction Analyzer."""

from pathlib import Path

from analytics import category_totals, find_duplicates, find_outliers, make_flagger, running_balance
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
            elif choice == 4:
                if not transactions:
                    print("No valid transactions loaded. Use option 2 first.")
                    continue
                totals = category_totals(transactions)
                income = category_totals(item for item in transactions if item.is_income())
                expenses = category_totals(item for item in transactions if item.amount < 0)
                print(f"\n{'CATEGORY':<18} {'INCOME':>14} {'EXPENSES':>14} {'NET':>14}")
                for category, net in sorted(totals.items()):
                    print(f"{category:<18} {income.get(category, 0):>+14.2f} "
                          f"{expenses.get(category, 0):>+14.2f} {net:>+14.2f}")
                print("Income and expenses follow the actual amount signs. Duplicates are included.")
            elif choice == 5:
                if not transactions:
                    print("No valid transactions loaded. Use option 2 first.")
                    continue
                duplicates = find_duplicates(transactions)
                print(f"\nDuplicate occurrences after the first: {len(duplicates)}")
                for transaction in duplicates:
                    print(f"  {transaction.formatted()}")
                if not duplicates:
                    print("No duplicate transactions found.")
                print("All loaded transactions remain included in the ledger and totals.")
            elif choice == 6:
                if not transactions:
                    print("No valid transactions loaded. Use option 2 first.")
                    continue
                answer = input("Magnitude threshold [Enter for 1000]: ").strip()
                flag = make_flagger(answer if answer else 1000)
                flagged = [transaction for transaction in transactions if flag(transaction)]
                print(f"\nTransactions exceeding the magnitude threshold: {len(flagged)}")
                for transaction in flagged:
                    print(f"  {transaction.formatted()}")
                if not flagged:
                    print("No transactions exceed this threshold.")
                outliers = find_outliers(transactions)
                print(f"\nStatistical outliers (> 2 sample standard deviations): {len(outliers)}")
                for transaction in outliers:
                    print(f"  {transaction.formatted()}")
                if not outliers:
                    print("No statistical outliers found.")
                print("Statistics use signed amounts; the magnitude threshold is a separate rule.")
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
