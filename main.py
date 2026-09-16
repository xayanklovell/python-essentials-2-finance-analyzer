"""Main menu for the Personal Finance Transaction Analyzer."""


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
    1: "Not implemented yet: generate the messy sample file in parser.py.",
    2: "Not implemented yet: load and validate transactions in parser.py.",
    3: "Not implemented yet: build the running-balance generator in analytics.py.",
    4: "Not implemented yet: calculate category totals in analytics.py.",
    5: "Not implemented yet: detect duplicate transactions in analytics.py.",
    6: "Not implemented yet: flag unusual transactions in analytics.py.",
    7: "Not implemented yet: write the monthly summary in reporting.py.",
    8: "No tests added yet. Write assertions in tests.py, then connect this option.",
}


def main():
    """Keep showing the menu until the user exits."""
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

        print(PENDING_MESSAGES[choice])


if __name__ == "__main__":
    main()
