import json
import os
from datetime import datetime, timedelta

class DebtTracker:
    def __init__(self, filename='debts.json'):
        self.filename = filename
        self.debts = {}
        self.load_debts()
    
    def load_debts(self):
        """Load debt data from file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.debts = data
        else:
            self.debts = {}
    
    def save_debts(self):
        """Save debt data to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.debts, f, indent=4)
    
    def record_debt(self, user_id, amount):
        """Record debt when user goes negative"""
        if user_id not in self.debts:
            self.debts[user_id] = {
                'amount': float(amount),
                'created_at': datetime.now().isoformat(),
                'deadline': (datetime.now() + timedelta(days=28)).isoformat(),
                'status': 'active'
            }
            self.save_debts()
    
    def clear_debt(self, user_id):
        """Clear debt when user pays back"""
        if user_id in self.debts:
            self.debts[user_id]['status'] = 'cleared'
            self.debts[user_id]['cleared_at'] = datetime.now().isoformat()
            self.save_debts()
    
    def get_debt(self, user_id):
        """Get debt info for user"""
        return self.debts.get(user_id, None)
    
    def get_debt_status(self, user_id):
        """Check if debt is active, cleared, or overdue"""
        debt = self.get_debt(user_id)
        
        if not debt:
            return {
                'has_debt': False,
                'status': 'none'
            }
        
        if debt['status'] == 'cleared':
            return {
                'has_debt': False,
                'status': 'cleared'
            }
        
        deadline = datetime.fromisoformat(debt['deadline'])
        now = datetime.now()
        days_remaining = (deadline - now).days
        
        if days_remaining < 0:
            status = 'overdue'
        elif days_remaining == 0:
            status = 'due_today'
        else:
            status = 'active'
        
        return {
            'has_debt': True,
            'status': status,
            'amount': debt['amount'],
            'created_at': debt['created_at'],
            'deadline': debt['deadline'],
            'days_remaining': max(0, days_remaining),
            'overdue_by': abs(days_remaining) if days_remaining < 0 else 0
        }
    
    def is_in_debt(self, user_id):
        """Check if user currently has active debt"""
        status = self.get_debt_status(user_id)
        return status['has_debt'] and status['status'] in ['active', 'due_today', 'overdue']
    
    def get_all_debts(self):
        """Get all debts"""
        return self.debts
