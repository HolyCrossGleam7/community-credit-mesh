import bluetooth
import json
import threading
from datetime import datetime

class BluetoothManager:
    def __init__(self):
        self.server_socket = None
        self.client_sockets = {}
        self.listening = False
        self.peer_devices = {}
        self.callbacks = {
            'on_peer_found': None,
            'on_peer_connected': None,
            'on_peer_disconnected': None,
            'on_data_received': None,
            'on_error': None
        }
        
    def set_callback(self, event, callback):
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def scan_for_devices(self, timeout=5):
        try:
            nearby_devices = bluetooth.discover_devices(duration=timeout, lookup_names=True)
            for addr, name in nearby_devices:
                device_info = {
                    'address': addr,
                    'name': name,
                    'timestamp': datetime.now().isoformat(),
                    'connected': False
                }
                self.peer_devices[addr] = device_info
                if self.callbacks['on_peer_found']:
                    self.callbacks['on_peer_found'](device_info)
            return self.peer_devices
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Scan failed: {str(e)}")
            return {}
    
    def start_server(self, port=1, uuid='94f39df5-bcbe-4f60-b212-1234567890ab'):
        try:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", port))
            self.server_socket.listen(1)
            self.listening = True
            listen_thread = threading.Thread(target=self._accept_connections, daemon=True)
            listen_thread.start()
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Server start failed: {str(e)}")
            return False
    
    def _accept_connections(self):
        while self.listening:
            try:
                client_socket, client_info = self.server_socket.accept()
                peer_addr = client_info[0]
                self.client_sockets[peer_addr] = client_socket
                if self.callbacks['on_peer_connected']:
                    self.callbacks['on_peer_connected']({'address': peer_addr})
                client_thread = threading.Thread(target=self._receive_data, args=(peer_addr, client_socket), daemon=True)
                client_thread.start()
            except Exception as e:
                if self.listening:
                    if self.callbacks['on_error']:
                        self.callbacks['on_error'](f"Accept failed: {str(e)}")
    
    def connect_to_peer(self, peer_address):
        try:
            client_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            client_socket.connect((peer_address, 1))
            self.client_sockets[peer_address] = client_socket
            if peer_address in self.peer_devices:
                self.peer_devices[peer_address]['connected'] = True
            if self.callbacks['on_peer_connected']:
                self.callbacks['on_peer_connected']({'address': peer_address})
            receive_thread = threading.Thread(target=self._receive_data, args=(peer_address, client_socket), daemon=True)
            receive_thread.start()
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Connection failed: {str(e)}")
            return False
    
    def _receive_data(self, peer_addr, socket):
        try:
            while True:
                data = socket.recv(1024)
                if not data:
                    break
                try:
                    message = json.loads(data.decode('utf-8'))
                    if self.callbacks['on_data_received']:
                        self.callbacks['on_data_received']({'from': peer_addr, 'data': message})
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pass
        finally:
            self.disconnect_peer(peer_addr)
    
    def send_data(self, peer_address, data):
        try:
            if peer_address not in self.client_sockets:
                raise Exception(f"Not connected to {peer_address}")
            socket = self.client_sockets[peer_address]
            message = json.dumps(data).encode('utf-8')
            socket.send(message)
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Send failed: {str(e)}")
            return False
    
    def broadcast_data(self, data):
        success_count = 0
        for peer_addr in list(self.client_sockets.keys()):
            if self.send_data(peer_addr, data):
                success_count += 1
        return success_count
    
    def disconnect_peer(self, peer_address):
        try:
            if peer_address in self.client_sockets:
                self.client_sockets[peer_address].close()
                del self.client_sockets[peer_address]
            if peer_address in self.peer_devices:
                self.peer_devices[peer_address]['connected'] = False
            if self.callbacks['on_peer_disconnected']:
                self.callbacks['on_peer_disconnected']({'address': peer_address})
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Disconnect failed: {str(e)}")
            return False
    
    def disconnect_all(self):
        for peer_addr in list(self.client_sockets.keys()):
            self.disconnect_peer(peer_addr)
    
    def stop_server(self):
        try:
            self.listening = False
            if self.server_socket:
                self.server_socket.close()
            self.disconnect_all()
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Stop server failed: {str(e)}")
            return False
    
    def get_connected_peers(self):
        return list(self.client_sockets.keys())
    
    def get_peer_info(self, peer_address=None):
        if peer_address:
            return self.peer_devices.get(peer_address, None)
        return self.peer_devices
