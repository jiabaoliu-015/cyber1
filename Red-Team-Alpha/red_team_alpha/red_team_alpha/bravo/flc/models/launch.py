from datetime import datetime

class LaunchAuthorization:
    """
    Archived launch paperwork.
    """

    def __init__(self, operation="Iron Ledger"):
        self.operation = operation
        self.timestamp = datetime.utcnow()

    def review(self):
        return (
            f"Operation: {self.operation}\n"
            "Archived authorization verified."
        )