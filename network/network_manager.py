from .bluetooth_manager import BluetoothManager
from .wifi_discovery import WiFiDiscovery
from .wifi_server import WiFiServer
from .wifi_client import WiFiClient
from datetime import datetime

class NetworkManager:
    def __init__(self, device_name="CCM-Device"):
        self.device_name = device_name
        
        # Initialize all network types
        self.bluetooth = BluetoothManager()
        self.wifi_discovery = WiFiDiscovery(device_name)
        self.wifi_server = WiFiServer()
        self.wifi_client = WiFiClient()
        
        self.active_connections = {}  # Track all connections
        self.callbacks = {
            'on_connection_changed': None,
            'on_data_received': None,
            'on_error': None
        }
        
        self._setup_callbacks()
    
    def set_callback(self, event, callback):
        """Set callback for events"""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def _setup_callbacks(self):
        """Setup callbacks for all network types"""
        # Bluetooth callbacks
        self.bluetooth.set_callback('on_data_received', self._on_data_received)
        self.bluetooth.set_callback('on_error', self._on_error)
        
        # WiFi Server callbacks
        self.wifi_server.set_callback('on_data_received', self._on_data_received)
        self.wifi_server.set_callback('on_error', self._on_error)
        
        # WiFi Client callbacks
        self.wifi_client.set_callback('on_data_received', self._on_data_received)
        self.wifi_client.set_callback('on_error', self._on_error)
        
        # WiFi Discovery callbacks
        self.wifi_discovery.set_callback('on_device_found', self._on_wifi_device_found)
        self.wifi_discovery.set_callback('on_error', self._on_error)
    
    def start_all_servers(self):
        """Start all server types"""
        bt_result = self.bluetooth.start_server()
        wifi_result = self.wifi_server.start()
        self.wifi_discovery.start_discovery()
        
        return bt_result and wifi_result
    
    def stop_all_servers(self):
        """Stop all servers"""
        self.bluetooth.stop_server()
        self.wifi_server.stop()
        self.wifi_discovery.stop_discovery()
        self.wifi_client.disconnect()
    
    def scan_devices(self):
        """Scan for devices on all networks"""
        devices = {
            'bluetooth': self.bluetooth.scan_for_devices(),
            'wifi': self.wifi_discovery.get_discovered_devices()
        }
        return devices
    
    def connect_bluetooth(self, peer_address):
        """Connect via Bluetooth"""
        return self.bluetooth.connect_to_peer(peer_address)
    
    def connect_wifi(self, server_ip):
        """Connect via WiFi"""
        return self.wifi_client.connect(server_ip)
    
    def broadcast_data(self, data):
        """Broadcast data on all active networks"""
        results = {
            'bluetooth': self.bluetooth.broadcast_data(data),
            'wifi': self.wifi_server.broadcast_data(data),
            'wifi_client': 1 if self.wifi_client.send_data(data) else 0
        }
        return results
    
    def disconnect_all(self):
        """Disconnect all connections"""
        self.bluetooth.disconnect_all()
        self.wifi_server.disconnect_all()
        self.wifi_client.disconnect()
    
    def get_all_connections(self):
        """Get all active connections"""
        connections = {
            'bluetooth_peers': self.bluetooth.get_connected_peers(),
            'wifi_clients': self.wifi_server.get_connected_clients(),
            'wifi_server': self.wifi_client.connected_server_ip if self.wifi_client.connected else None
        }
        return connections
    
    def get_connection_status(self):
        """Get overall connection status"""
        bt_count = len(self.bluetooth.get_connected_peers())
        wifi_server_count = len(self.wifi_server.get_connected_clients())
        wifi_client_connected = self.wifi_client.is_connected()
        
        return {
            'bluetooth_connected': bt_count,
            'wifi_server_clients': wifi_server_count,
            'wifi_client_connected': wifi_client_connected,
            'total_connections': bt_count + wifi_server_count + (1 if wifi_client_connected else 0)
        }
    
    def _on_data_received(self, message):
        """Handle data received from any network"""
        if self.callbacks['on_data_received']:
            self.callbacks['on_data_received'](message)
    
    def _on_wifi_device_found(self, device_info):
        """Handle WiFi device discovery"""
        # Could trigger UI update or auto-connect
        pass
    
    def _on_error(self, error):
        """Handle errors from any network"""
        if self.callbacks['on_error']:
            self.callbacks['on_error'](error)
