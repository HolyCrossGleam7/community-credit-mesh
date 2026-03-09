import json
from datetime import datetime

class TransactionBroadcaster:
    def __init__(self, network_sync, bluetooth_manager):
        self.network_sync = network_sync
        self.bluetooth_manager = bluetooth_manager
        self.broadcast_history = []
    
    def broadcast_transaction(self, sender, receiver, amount, description=""):
        """Create and broadcast a transaction to all peers"""
        # Create transaction packet
        transaction_packet = self.network_sync.create_transaction_packet(
            sender, receiver, amount, description
        )
        
        return self.broadcast_packet(transaction_packet)

    def broadcast_packet(self, transaction_packet):
        """Broadcast a pre-built (and optionally pre-signed) transaction packet."""
        # Broadcast to all connected peers
        peers_count = self.bluetooth_manager.broadcast_data(transaction_packet)
        
        # Record broadcast
        self.broadcast_history.append({
            'transaction_id': transaction_packet['transaction_id'],
            'sender': transaction_packet['sender'],
            'receiver': transaction_packet['receiver'],
            'amount': transaction_packet['amount'],
            'peers_count': peers_count,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'transaction_id': transaction_packet['transaction_id'],
            'peers_notified': peers_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_broadcast_history(self):
        """Get history of all broadcasts"""
        return self.broadcast_history
    
    def get_recent_broadcasts(self, limit=10):
        """Get recently broadcasted transactions"""
        return self.broadcast_history[-limit:]
