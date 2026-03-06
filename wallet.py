# wallet.py

class Wallet:
    def __init__(self):
        self.balances = {}

    def create_wallet(self, user_id):
        if user_id not in self.balances:
            self.balances[user_id] = 0.0
            return True
        return False

    def deposit(self, user_id, amount):
        if user_id in self.balances and amount > 0:
            self.balances[user_id] += amount
            return True
        return False

    def withdraw(self, user_id, amount):
        if user_id in self.balances and 0 < amount <= self.balances[user_id]:
            self.balances[user_id] -= amount
            return True
        return False

    def get_balance(self, user_id):
        return self.balances.get(user_id, None)