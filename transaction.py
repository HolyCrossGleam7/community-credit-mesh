class Transaction:
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = None  # Will be assigned later

    def validate_transaction(self):
        # Here we might have code to validate if the sender has enough balance
        pass

    def execute(self):
        # Here we might have code to execute the transaction
        pass


class MultiPeerTransaction:
    def __init__(self, sender, receivers, amounts):
        self.sender = sender
        self.receivers = receivers
        self.amounts = amounts

    def validate_transactions(self):
        # Validate each individual transaction
        for receiver, amount in zip(self.receivers, self.amounts):
            # Here we might have code to validate each transaction
            pass

    def execute(self):
        # Execute all transactions
        for receiver, amount in zip(self.receivers, self.amounts):
            transaction = Transaction(self.sender, receiver, amount)
            transaction.execute()  # Execute the individual transaction
