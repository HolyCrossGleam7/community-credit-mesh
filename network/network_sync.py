import json
import sys
import os
from datetime import datetime

import security
import trusted_peers as trusted_peers_mod

class NetworkSync:
    def __init__(self):
        self.sync_history = []
        self.pending_transactions = []
        # Set via set_signing_key() after the user logs in.
        self._private_key = None
        self._public_key_hex = None

    def set_signing_key(self, private_key, public_key_hex: str) -> None:
        """Configure the local user's Ed25519 signing keypair."""
        self._private_key = private_key
        self._public_key_hex = public_key_hex

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
        # Sign the packet if a keypair is available.
        if self._private_key is not None and self._public_key_hex:
            security.sign_packet(transaction, self._private_key, self._public_key_hex)
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
        """Validate, verify, and record an incoming transaction.

        Returns:
            (success: bool, message: str)
        """
        try:
            if not self._validate_transaction(transaction_data):
                return False, "Invalid transaction structure."
            if self._is_duplicate(transaction_data):
                return False, "Duplicate transaction."

            # --- Signature verification ----------------------------------
            sig_valid, sig_msg = security.verify_packet(transaction_data)
            if not sig_valid:
                return False, f"Blocked — {sig_msg}"

            # --- Trust-on-first-use key pinning --------------------------
            sender = transaction_data.get("sender", "")
            incoming_key = transaction_data.get("public_key", "")

            pinned_key = trusted_peers_mod.get_trusted_key(sender)
            if pinned_key is None:
                # First time we hear from this sender — pin their key.
                trusted_peers_mod.pin_key(sender, incoming_key)
            elif pinned_key != incoming_key:
                return (
                    False,
                    f"Blocked — public key for '{sender}' does not match pinned key. "
                    "If this peer changed devices, reset trust via the Peers tab.",
                )

            tx_id = transaction_data['transaction_id']
            self.sync_history.append(tx_id)
            return True, "OK"
        except Exception as e:
            print(f"Error processing transaction: {str(e)}")
            return False, f"Error: {e}"
    
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
