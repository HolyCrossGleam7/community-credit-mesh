# wallet.py

class Wallet:
    def __init__(self):
        self.balances = {}
    
    def create_wallet(self, user_id):
        """Create wallet starting at 0 balance"""
        if user_id not in self.balances:
            self.balances[user_id] = 0.0
            return True
        return False
    
    def deposit(self, user_id, amount):
        """Add credits to wallet"""
        if user_id in self.balances and amount > 0:
            self.balances[user_id] += amount
            return True
        return False
    
    def withdraw(self, user_id, amount):
        """Withdraw credits (can go negative = debt)"""
        if user_id in self.balances and amount > 0:
            self.balances[user_id] -= amount
            return True
        return False
    
    def send_credits(self, sender_id, receiver_id, amount):
        """Send credits between wallets (allows debt)"""
        if sender_id not in self.balances or receiver_id not in self.balances:
            return False
        if amount <= 0:
            return False
        self.balances[sender_id] -= amount
        self.balances[receiver_id] += amount
        return True
    
    def get_balance(self, user_id):
        """Get user balance (can be negative)"""
        return self.balances.get(user_id, None)
    
    def set_balance(self, user_id, amount):
        """Set balance for user"""
        if user_id in self.balances:
            self.balances[user_id] = float(amount)
            return True
        return False
    
    def get_all_balances(self):
        """Get all balances"""
        return self.balances
    
    def is_in_debt(self, user_id):
        """Check if user is in debt"""
        balance = self.get_balance(user_id)
        return balance is not None and balance < 0
    
    def get_debt_amount(self, user_id):
        """Get debt amount if negative"""
        balance = self.get_balance(user_id)
        if balance is not None and balance < 0:
            return abs(balance)
        return 0.0
