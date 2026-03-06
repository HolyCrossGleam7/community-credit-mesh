import json
import os
import datetime

class Ledger:
    def __init__(self, filename='ledger.json'):
        self.filename = filename
        self.load_ledger()

    def load_ledger(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.ledger = json.load(f)
        else:
            self.ledger = {'transactions': [], 'balances': {}} 

    def record_transaction(self, transaction):
        self.ledger['transactions'].append(transaction)
        self.update_balances(transaction)
        self.save_ledger()

    def update_balances(self, transaction):
        # Assuming transaction is a dict with 'user' and 'amount' keys
        user = transaction['user']
        amount = transaction['amount']
        if user not in self.ledger['balances']:
            self.ledger['balances'][user] = 0
        self.ledger['balances'][user] += amount

    def get_balance(self, user):
        return self.ledger['balances'].get(user, 0)

    def get_all_balances(self):
        return self.ledger['balances']

    def get_transaction_history(self):
        return self.ledger['transactions']

    def validate_transaction(self, transaction):
        # Basic validation logic (to be expanded)
        return 'user' in transaction and 'amount' in transaction

    def export_ledger(self, format='json'):
        if format == 'json':
            with open(self.filename, 'w') as f:
                json.dump(self.ledger, f, indent=4)

# Example Usage:
# ledger = Ledger()
# ledger.record_transaction({'user': 'Alice', 'amount': 100})
# print(ledger.get_balance('Alice'))