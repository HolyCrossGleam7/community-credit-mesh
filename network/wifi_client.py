import socket
import threading
import json
from datetime import datetime

class WiFiClient:
    def __init__(self):
        self.socket = None
        self.connected = False
        self.connected_server_ip = None
        self.callbacks = {
            'on_connected': None,
            'on_disconnected': None,
            'on_data_received': None,
            'on_error': None
        }
    
    def set_callback(self, event, callback):
        """Set callback for events"""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def connect(self, server_ip, server_port=5556):
        """Connect to a WiFi server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((server_ip, server_port))
            self.connected = True
            self.connected_server_ip = server_ip
            
            if self.callbacks['on_connected']:
                self.callbacks['on_connected']({'server_ip': server_ip})
            
            # Start receiving data
            receive_thread = threading.Thread(
                target=self._receive_data,
                daemon=True
            )
            receive_thread.start()
            
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Connection failed: {str(e)}")
            return False
    
    def _receive_data(self):
        """Receive data from server"""
        try:
            while self.connected:
                data = self.socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    if self.callbacks['on_data_received']:
                        self.callbacks['on_data_received']({
                            'from': self.connected_server_ip,
                            'data': message
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            if self.connected:
                if self.callbacks['on_error']:
                    self.callbacks['on_error'](f"Receive error: {str(e)}")
        finally:
            self.disconnect()
    
    def send_data(self, data):
        """Send data to server"""
        try:
            if not self.connected:
                raise Exception("Not connected to server")
            
            message = json.dumps(data).encode('utf-8')
            self.socket.send(message)
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Send failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        try:
            self.connected = False
            if self.socket:
                self.socket.close()
            
            if self.callbacks['on_disconnected']:
                self.callbacks['on_disconnected']({'server_ip': self.connected_server_ip})
            
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Disconnect failed: {str(e)}")
            return False
    
    def is_connected(self):
        """Check if connected"""
        return self.connected
