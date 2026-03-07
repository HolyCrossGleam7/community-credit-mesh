import json
import os
from datetime import datetime

class CommonFund:
    def __init__(self, filename='common_fund.json'):
        self.filename = filename
        self.load_fund()

    def load_fund(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.fund_data = json.load(f)
        else:
            self.fund_data = {
                'fund_balance': 0.0,
                'contributors': {},
                'contributions': []
            }

    def save_fund(self):
        with open(self.filename, 'w') as f:
            json.dump(self.fund_data, f, indent=4)

    def contribute(self, user, amount):
        """Add a contribution to the common fund"""
        if amount <= 0:
            raise ValueError("Contribution amount must be positive.")
        
        self.fund_data['fund_balance'] += amount
        
        if user not in self.fund_data['contributors']:
            self.fund_data['contributors'][user] = 0.0
        
        self.fund_data['contributors'][user] += amount
        
        contribution_record = {
            'user': user,
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }
        self.fund_data['contributions'].append(contribution_record)
        
        self.save_fund()
        return self.fund_data['fund_balance']

    def get_balance(self):
        """Get the total balance of the common fund"""
        return self.fund_data['fund_balance']

    def get_contributors(self):
        """Get all contributors and their contribution amounts"""
        return self.fund_data['contributors']

    def distribute_funds(self, amount_per_user):
        """Distribute equal amounts to all contributors"""
        if amount_per_user <= 0:
            raise ValueError("Amount to distribute must be positive.")
        
        if amount_per_user * len(self.fund_data['contributors']) > self.fund_data['fund_balance']:
            raise ValueError("Insufficient funds in the common fund.")

        for user in self.fund_data['contributors']:
            self.fund_data['fund_balance'] -= amount_per_user
            if user not in self.fund_data['contributors']:
                self.fund_data['contributors'][user] = 0.0
            self.fund_data['contributors'][user] -= amount_per_user

        self.save_fund()
        return self.fund_data['fund_balance']

    def get_contribution_history(self):
        """Get the complete contribution history"""
        return self.fund_data['contributions']