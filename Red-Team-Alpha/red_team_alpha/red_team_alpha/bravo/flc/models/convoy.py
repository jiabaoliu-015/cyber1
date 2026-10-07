from datetime import datetime

class ConvoyTransfer:
    """
    Archived convoy records.
    """

    def __init__(self, convoy="C-17"):
        self.convoy = convoy
        self.time = datetime.utcnow()

    def status(self):
        return (
            f"Convoy: {self.convoy}\n"
            "Transfer completed."
        )