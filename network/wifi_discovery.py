import socket
import threading
from datetime import datetime
import json

class WiFiDiscovery:
    def __init__(self, device_name="CCM-Device"):
        self.device_name = device_name
        self.discovered_devices = {}
        self.callbacks = {
            'on_device_found': None,
            'on_device_lost': None,
            'on_error': None
        }
        self.scanning = False
    
    def set_callback(self, event, callback):
        """Set callback for events"""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def get_local_ip(self):
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Failed to get IP: {str(e)}")
            return "127.0.0.1"
    
    def broadcast_presence(self, port=5555):
        """Broadcast presence on local network"""
        try:
            broadcast_data = {
                'type': 'presence',
                'device_name': self.device_name,
                'ip': self.get_local_ip(),
                'port': port,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            message = json.dumps(broadcast_data).encode('utf-8')
            sock.sendto(message, ('<broadcast>', 5555))
            sock.close()
            
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Broadcast failed: {str(e)}")
            return False
    
    def start_discovery(self, port=5555):
        """Start listening for device broadcasts"""
        self.scanning = True
        discovery_thread = threading.Thread(
            target=self._listen_for_broadcasts,
            args=(port,),
            daemon=True
        )
        discovery_thread.start()
    
    def _listen_for_broadcasts(self, port):
        """Listen for device broadcasts"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', port))
            
            while self.scanning:
                try:
                    data, addr = sock.recvfrom(1024)
                    message = json.loads(data.decode('utf-8'))
                    
                    if message['type'] == 'presence':
                        device_info = {
                            'name': message['device_name'],
                            'ip': message['ip'],
                            'port': message['port'],
                            'discovered_at': datetime.now().isoformat(),
                            'last_seen': datetime.now().isoformat()
                        }
                        
                        self.discovered_devices[message['ip']] = device_info
                        
                        if self.callbacks['on_device_found']:
                            self.callbacks['on_device_found'](device_info)
                except json.JSONDecodeError:
                    pass
                except Exception as e:
                    if self.scanning:
                        pass
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Discovery error: {str(e)}")
        finally:
            sock.close()
    
    def stop_discovery(self):
        """Stop discovery"""
        self.scanning = False
    
    def get_discovered_devices(self):
        """Get all discovered devices"""
        return self.discovered_devices
    
    def get_device_by_ip(self, ip):
        """Get device info by IP"""
        return self.discovered_devices.get(ip, None)
