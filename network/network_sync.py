import json
from datetime import datetime

class NetworkSync:
    def __init__(self):
        self.sync_history = []
        self.pending_transactions = []
        
    def create_transaction_packet(self, sender, receiver, amount, description=""):
        transaction = {
            'type': 'transaction',
            'sender': sender,
            'receiver': receiver,
            'amount': float(amount),
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'transaction_id': self._generate_tx_id(sender, receiver, amount),
            'version': '1.0'
        }
        return transaction
    
    def create_sync_request(self, device_name, balance=None):
        packet = {
            'type': 'sync_request',
            'device_name': device_name,
            'timestamp': datetime.now().isoformat(),
            'balance': balance
        }
        return packet
    
    def create_sync_response(self, transactions, balances):
        packet = {
            'type': 'sync_response',
            'transactions': transactions,
            'balances': balances,
            'timestamp': datetime.now().isoformat()
        }
        return packet
    
    def process_received_transaction(self, transaction_data):
        try:
            if not self._validate_transaction(transaction_data):
                return False
            if self._is_duplicate(transaction_data):
                return False
            tx_id = transaction_data['transaction_id']
            self.sync_history.append(tx_id)
            return True
        except Exception as e:
            print(f"Error processing transaction: {str(e)}")
            return False
    
    def queue_transaction(self, sender, receiver, amount, description=""):
        transaction = self.create_transaction_packet(sender, receiver, amount, description)
        self.pending_transactions.append(transaction)
        return transaction
    
    def get_pending_transactions(self):
        return self.pending_transactions.copy()
    
    def clear_pending_transactions(self):
        self.pending_transactions.clear()
    
    def _validate_transaction(self, transaction):
        required_fields = ['sender', 'receiver', 'amount', 'timestamp', 'transaction_id']
        for field in required_fields:
            if field not in transaction:
                return False
        if transaction['amount'] <= 0:
            return False
        if transaction['sender'] == transaction['receiver']:
            return False
        return True
    
    def _is_duplicate(self, transaction):
        tx_id = transaction['transaction_id']
        return tx_id in self.sync_history
    
    def _generate_tx_id(self, sender, receiver, amount):
        import hashlib
        data = f"{sender}{receiver}{amount}{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
