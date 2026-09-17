"""Transaction classes. Keep file and menu logic out of this module."""

import math


class Transaction:
    """Store one transaction and identify income from its amount."""

    # Shared by every Transaction object created during the current run.
    total_transactions = 0

    def __init__(self, date, description, amount, category):
        """Set up a transaction; calendar-date validation belongs to the parser."""
        for label, value in (("date", date), ("description", description), ("category", category)):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} must be nonempty text")

        # float(True) is 1.0, but a boolean is not a valid transaction amount.
        if isinstance(amount, bool):
            raise ValueError("amount must be a number, not a boolean")
        try:
            amount = float(amount)
        except (TypeError, ValueError, OverflowError) as error:
            raise ValueError("amount must be a number") from error
        if not math.isfinite(amount):
            raise ValueError("amount must be finite; NaN and infinity are invalid")

        self.date = date.strip()
        self.description = description.strip()
        self.amount = amount
        self.category = category.strip().upper()

        # Invalid inputs never reach this line, so they do not increase the count.
        Transaction.total_transactions += 1

    def is_income(self):
        """Positive amounts are income; negative amounts and zero are not."""
        return self.amount > 0

    def formatted(self):
        """Show the date, description, signed amount, and category on one line."""
        return f"{self.date} {self.description} {self.amount:+.2f} {self.category}"

    def __str__(self):
        """Use the same readable format when the transaction is printed."""
        return self.formatted()


class RecurringTransaction(Transaction):
    """A transaction with a recurring interval, such as monthly rent."""

    def __init__(self, date, description, amount, category, interval="monthly"):
        # Check the extra field first, so an invalid interval is never counted.
        if not isinstance(interval, str) or not interval.strip():
            raise ValueError("interval must be nonempty text")
        super().__init__(date, description, amount, category)
        self.interval = interval.strip().lower()

    def formatted(self):
        """Extend the parent's display with the recurrence interval."""
        return f"{super().formatted()} [recurs {self.interval}]"
