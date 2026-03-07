from datetime import datetime

class Transaction:
    def __init__(self, sender, receiver, amount, description=""):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.description = description
        self.transaction_id = None
        self.timestamp = datetime.now().isoformat()

    def validate_transaction(self):
        """Validate transaction"""
        if self.amount <= 0:
            return False
        if self.sender == self.receiver:
            return False
        return True

    def execute(self):
        """Execute the transaction"""
        if self.validate_transaction():
            self.transaction_id = self._generate_id()
            return True
        return False

    def _generate_id(self):
        """Generate transaction ID"""
        import hashlib
        data = f"{self.sender}{self.receiver}{self.amount}{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def broadcast_to_peers(self, broadcaster):
        """Broadcast transaction to peers"""
        if not self.transaction_id:
            self.execute()
        
        result = broadcaster.broadcast_transaction(
            self.sender, self.receiver, self.amount, self.description
        )
        return result


class MultiPeerTransaction:
    def __init__(self, sender, receivers, amounts):
        self.sender = sender
        self.receivers = receivers
        self.amounts = amounts

    def validate_transactions(self):
        """Validate each individual transaction"""
        for receiver, amount in zip(self.receivers, self.amounts):
            if amount <= 0 or self.sender == receiver:
                return False
        return True

    def execute(self):
        """Execute all transactions"""
        if not self.validate_transactions():
            return False
        
        for receiver, amount in zip(self.receivers, self.amounts):
            transaction = Transaction(self.sender, receiver, amount)
            transaction.execute()
        
        return True
