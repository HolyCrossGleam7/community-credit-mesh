import socket
import threading
import json
from datetime import datetime

class WiFiServer:
    def __init__(self, port=5556):
        self.port = port
        self.server_socket = None
        self.listening = False
        self.client_sockets = {}
        self.callbacks = {
            'on_client_connected': None,
            'on_client_disconnected': None,
            'on_data_received': None,
            'on_error': None
        }
    
    def set_callback(self, event, callback):
        """Set callback for events"""
        if event in self.callbacks:
            self.callbacks[event] = callback
    
    def start(self):
        """Start WiFi server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            self.listening = True
            
            listen_thread = threading.Thread(
                target=self._accept_clients,
                daemon=True
            )
            listen_thread.start()
            
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Server start failed: {str(e)}")
            return False
    
    def _accept_clients(self):
        """Accept incoming client connections"""
        while self.listening:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_ip = client_address[0]
                
                self.client_sockets[client_ip] = client_socket
                
                if self.callbacks['on_client_connected']:
                    self.callbacks['on_client_connected']({'ip': client_ip})
                
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_ip, client_socket),
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                if self.listening:
                    if self.callbacks['on_error']:
                        self.callbacks['on_error'](f"Accept failed: {str(e)}")
    
    def _handle_client(self, client_ip, client_socket):
        """Handle client connection"""
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                
                try:
                    message = json.loads(data.decode('utf-8'))
                    if self.callbacks['on_data_received']:
                        self.callbacks['on_data_received']({
                            'from': client_ip,
                            'data': message
                        })
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            pass
        finally:
            self.disconnect_client(client_ip)
    
    def send_data(self, client_ip, data):
        """Send data to a specific client"""
        try:
            if client_ip not in self.client_sockets:
                return False
            
            sock = self.client_sockets[client_ip]
            message = json.dumps(data).encode('utf-8')
            sock.send(message)
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Send failed: {str(e)}")
            return False
    
    def broadcast_data(self, data):
        """Send data to all connected clients"""
        success_count = 0
        for client_ip in list(self.client_sockets.keys()):
            if self.send_data(client_ip, data):
                success_count += 1
        return success_count
    
    def disconnect_client(self, client_ip):
        """Disconnect a client"""
        try:
            if client_ip in self.client_sockets:
                self.client_sockets[client_ip].close()
                del self.client_sockets[client_ip]
            
            if self.callbacks['on_client_disconnected']:
                self.callbacks['on_client_disconnected']({'ip': client_ip})
            
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Disconnect failed: {str(e)}")
            return False
    
    def disconnect_all(self):
        """Disconnect all clients"""
        for client_ip in list(self.client_sockets.keys()):
            self.disconnect_client(client_ip)
    
    def stop(self):
        """Stop the server"""
        try:
            self.listening = False
            if self.server_socket:
                self.server_socket.close()
            self.disconnect_all()
            return True
        except Exception as e:
            if self.callbacks['on_error']:
                self.callbacks['on_error'](f"Stop failed: {str(e)}")
            return False
    
    def get_connected_clients(self):
        """Get list of connected clients"""
        return list(self.client_sockets.keys())
