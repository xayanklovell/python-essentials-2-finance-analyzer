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

    # TODO: Add formatted() and __str__().


# TODO: Add RecurringTransaction using super() and a method override.
