import json
import os
from datetime import datetime

class PeerManager:
    def __init__(self, filename='peers.json'):
        self.filename = filename
        self.load_peers()
    
    def load_peers(self):
        """Load peer data from file"""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.peer_data = json.load(f)
        else:
            self.peer_data = {
                'known_peers': {},
                'connection_history': []
            }
    
    def save_peers(self):
        """Save peer data to file"""
        with open(self.filename, 'w') as f:
            json.dump(self.peer_data, f, indent=4)
    
    def add_peer(self, peer_address, peer_name, favorite=False):
        """Add a new peer or update existing"""
        if peer_address not in self.peer_data['known_peers']:
            self.peer_data['known_peers'][peer_address] = {
                'name': peer_name,
                'first_connected': datetime.now().isoformat(),
                'last_connected': datetime.now().isoformat(),
                'connection_count': 1,
                'favorite': favorite
            }
        else:
            peer = self.peer_data['known_peers'][peer_address]
            peer['last_connected'] = datetime.now().isoformat()
            peer['connection_count'] += 1
        
        self.save_peers()
    
    def record_connection(self, peer_address, peer_name, status='connected'):
        """Record a connection event"""
        self.add_peer(peer_address, peer_name)
        
        connection_record = {
            'peer_address': peer_address,
            'peer_name': peer_name,
            'status': status,
            'timestamp': datetime.now().isoformat()
        }
        self.peer_data['connection_history'].append(connection_record)
        self.save_peers()
    
    def get_peer(self, peer_address):
        """Get info about a specific peer"""
        return self.peer_data['known_peers'].get(peer_address, None)
    
    def get_all_peers(self):
        """Get all known peers"""
        return self.peer_data['known_peers']
    
    def get_favorite_peers(self):
        """Get favorite peers"""
        favorites = {}
        for addr, info in self.peer_data['known_peers'].items():
            if info.get('favorite', False):
                favorites[addr] = info
        return favorites
    
    def set_favorite(self, peer_address, favorite=True):
        """Mark peer as favorite"""
        if peer_address in self.peer_data['known_peers']:
            self.peer_data['known_peers'][peer_address]['favorite'] = favorite
            self.save_peers()
    
    def get_connection_history(self):
        """Get connection history"""
        return self.peer_data['connection_history']
    
    def get_recent_peers(self, limit=5):
        """Get recently connected peers"""
        history = self.peer_data['connection_history']
        recent = {}
        for record in history[-limit:]:
            peer_addr = record['peer_address']
            if peer_addr in self.peer_data['known_peers']:
                recent[peer_addr] = self.peer_data['known_peers'][peer_addr]
        return recent
