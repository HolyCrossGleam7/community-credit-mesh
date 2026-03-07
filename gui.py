import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QListWidget, 
                              QListWidgetItem, QTextEdit, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from datetime import datetime
from network.bluetooth_manager import BluetoothManager
from network.network_sync import NetworkSync
from network.transaction_broadcaster import TransactionBroadcaster
from peer_manager import PeerManager

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Community Credit Mesh - Desktop')
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize network components
        self.bt_manager = BluetoothManager()
        self.network_sync = NetworkSync()
        self.broadcaster = TransactionBroadcaster(self.network_sync, self.bt_manager)
        self.peer_manager = PeerManager()
        
        # Set up callbacks
        self.bt_manager.set_callback('on_peer_found', self.on_peer_found)
        self.bt_manager.set_callback('on_peer_connected', self.on_peer_connected)
        self.bt_manager.set_callback('on_peer_disconnected', self.on_peer_disconnected)
        self.bt_manager.set_callback('on_data_received', self.on_data_received)
        self.bt_manager.set_callback('on_error', self.on_network_error)
        
        self.current_user = None
        self.balance = 100
        self.server_running = False
        
        self.initUI()
    
    def initUI(self):
        """Initialize the user interface"""
        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.wallet_tab = self.create_wallet_tab()
        self.send_tab = self.create_send_tab()
        self.network_tab = self.create_network_tab()
        self.peers_tab = self.create_peers_tab()
        
        # Add tabs
        self.tabs.addTab(self.wallet_tab, "💳 Wallet")
        self.tabs.addTab(self.send_tab, "📤 Send")
        self.tabs.addTab(self.network_tab, "🌐 Network")
        self.tabs.addTab(self.peers_tab, "👥 Peers")
    
    def create_wallet_tab(self):
        """Create Wallet tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Welcome to Community Credit Mesh"))
        
        self.wallet_status = QLabel(f"Status: Not logged in")
        layout.addWidget(self.wallet_status)
        
        self.balance_label = QLabel(f"Balance: {self.balance} Credits")
        self.balance_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        layout.addWidget(self.balance_label)
        
        # Login section
        login_layout = QHBoxLayout()
        login_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        login_layout.addWidget(self.username_input)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)
        
        layout.addLayout(login_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_send_tab(self):
        """Create Send tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Send Credits"))
        
        layout.addWidget(QLabel("Recipient:"))
        self.recipient_input = QLineEdit()
        layout.addWidget(self.recipient_input)
        
        layout.addWidget(QLabel("Amount:"))
        self.amount_input = QLineEdit()
        layout.addWidget(self.amount_input)
        
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        layout.addWidget(self.description_input)
        
        send_btn = QPushButton("Send Credits")
        send_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        send_btn.clicked.connect(self.send_credits)
        layout.addWidget(send_btn)
        
        self.send_status = QLabel("")
        layout.addWidget(self.send_status)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_network_tab(self):
        """Create Network tab with Bluetooth controls"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Status
        layout.addWidget(QLabel("🌐 Bluetooth Network Status", ))
        self.network_status = QLabel("Status: ❌ Disconnected")
        self.network_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.network_status)
        
        # Server controls
        server_layout = QHBoxLayout()
        self.server_btn = QPushButton("▶ Start Server")
        self.server_btn.clicked.connect(self.toggle_server)
        self.server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        server_layout.addWidget(self.server_btn)
        
        scan_btn = QPushButton("🔍 Scan Devices")
        scan_btn.clicked.connect(self.scan_devices)
        scan_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        server_layout.addWidget(scan_btn)
        
        layout.addLayout(server_layout)
        
        # Available devices
        layout.addWidget(QLabel("Available Devices:"))
        self.device_list = QListWidget()
        layout.addWidget(self.device_list)
        
        # Connect button
        connect_btn = QPushButton("🔗 Connect Selected")
        connect_btn.clicked.connect(self.connect_device)
        connect_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(connect_btn)
        
        # Connected peers
        layout.addWidget(QLabel("Connected Peers:"))
        self.connected_peers_list = QListWidget()
        layout.addWidget(self.connected_peers_list)
        
        # Disconnect button
        disconnect_btn = QPushButton("❌ Disconnect Selected")
        disconnect_btn.clicked.connect(self.disconnect_device)
        disconnect_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        layout.addWidget(disconnect_btn)
        
        # Messages
        layout.addWidget(QLabel("Network Messages:"))
        self.network_messages = QTextEdit()
        self.network_messages.setReadOnly(True)
        self.network_messages.setMaximumHeight(150)
        layout.addWidget(self.network_messages)
        
        widget.setLayout(layout)
        return widget
    
    def create_peers_tab(self):
        """Create Peers tab for managing connections"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("👥 Connected Peers Management"))
        
        # Peer list
        layout.addWidget(QLabel("Known Peers:"))
        self.peers_list = QListWidget()
        layout.addWidget(self.peers_list)
        
        # Peer info
        layout.addWidget(QLabel("Peer Details:"))
        self.peer_details = QTextEdit()
        self.peer_details.setReadOnly(True)
        self.peer_details.setMaximumHeight(200)
        layout.addWidget(self.peer_details)
        
        # Mark favorite button
        fav_btn = QPushButton("⭐ Mark as Favorite")
        fav_btn.clicked.connect(self.mark_favorite)
        layout.addWidget(fav_btn)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_peers)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    # Network Methods
    def toggle_server(self):
        """Start/Stop Bluetooth server"""
        if not self.server_running:
            self.bt_manager.start_server()
            self.server_running = True
            self.server_btn.setText("⏹ Stop Server")
            self.server_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 10px;")
            self.log_network_message("✅ Bluetooth server started")
        else:
            self.bt_manager.stop_server()
            self.server_running = False
            self.server_btn.setText("▶ Start Server")
            self.server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
            self.log_network_message("⏹ Bluetooth server stopped")
    
    def scan_devices(self):
        """Scan for Bluetooth devices"""
        self.log_network_message("🔍 Scanning for devices...")
        devices = self.bt_manager.scan_for_devices(timeout=5)
        
        self.device_list.clear()
        for addr, info in devices.items():
            item_text = f"{info['name']} ({addr})"
            item = QListWidgetItem(item_text)
            self.device_list.addItem(item)
        
        self.log_network_message(f"✅ Found {len(devices)} devices")
    
    def connect_device(self):
        """Connect to selected device"""
        selected = self.device_list.currentItem()
        if not selected:
            self.log_network_message("⚠️ Please select a device")
            return
        
        text = selected.text()
        addr = text.split('(')[1].rstrip(')')
        
        self.log_network_message(f"🔗 Connecting to {addr}...")
        success = self.bt_manager.connect_to_peer(addr)
        
        if success:
            self.log_network_message(f"✅ Connected to {addr}")
        else:
            self.log_network_message(f"❌ Failed to connect to {addr}")
    
    def disconnect_device(self):
        """Disconnect from selected peer"""
        selected = self.connected_peers_list.currentItem()
        if not selected:
            self.log_network_message("⚠️ Please select a peer")
            return
        
        peer = selected.text()
        self.bt_manager.disconnect_peer(peer)
        self.log_network_message(f"✅ Disconnected from {peer}")
    
    # Transaction Methods
    def send_credits(self):
        """Send credits and broadcast to peers"""
        if not self.current_user:
            self.send_status.setText("❌ Please login first")
            self.send_status.setStyleSheet("color: red;")
            return
        
        recipient = self.recipient_input.text()
        amount = self.amount_input.text()
        description = self.description_input.text()
        
        if not recipient or not amount:
            self.send_status.setText("❌ Please fill in all fields")
            self.send_status.setStyleSheet("color: red;")
            return
        
        try:
            amount = float(amount)
            
            # Validate balance
            if amount > self.balance:
                self.send_status.setText("❌ Insufficient balance")
                self.send_status.setStyleSheet("color: red;")
                return
            
            # Update local balance
            self.balance -= amount
            self.balance_label.setText(f"Balance: {self.balance} Credits")
            
            # Broadcast transaction to peers
            result = self.broadcaster.broadcast_transaction(
                self.current_user, recipient, amount, description
            )
            
            self.send_status.setText(f"✅ Sent {amount} credits to {recipient} (notified {result['peers_notified']} peers)")
            self.send_status.setStyleSheet("color: green;")
            
            # Clear inputs
            self.recipient_input.clear()
            self.amount_input.clear()
            self.description_input.clear()
            
            self.log_network_message(f"📤 Broadcasted transaction to {result['peers_notified']} peers")
            
        except ValueError:
            self.send_status.setText("❌ Invalid amount")
            self.send_status.setStyleSheet("color: red;")
    
    # Peer Management Methods
    def refresh_peers(self):
        """Refresh peer list"""
        self.peers_list.clear()
        peers = self.peer_manager.get_all_peers()
        
        for addr, info in peers.items():
            favorite = "⭐" if info.get('favorite') else "  "
            item_text = f"{favorite} {info['name']} ({addr})"
            item = QListWidgetItem(item_text)
            self.peers_list.addItem(item)
    
    def mark_favorite(self):
        """Mark selected peer as favorite"""
        selected = self.peers_list.currentItem()
        if not selected:
            return
        
        text = selected.text()
        addr = text.split('(')[1].rstrip(')')
        
        peer = self.peer_manager.get_peer(addr)
        if peer:
            is_favorite = not peer.get('favorite', False)
            self.peer_manager.set_favorite(addr, is_favorite)
            self.refresh_peers()
    
    # Callbacks
    def on_peer_found(self, peer_info):
        """Callback when peer is found"""
        self.log_network_message(f"🔍 Found: {peer_info['name']}")
    
    def on_peer_connected(self, peer_info):
        """Callback when peer connects"""
        addr = peer_info['address']
        self.update_peers_list()
        self.update_network_status()
        self.log_network_message(f"✅ Connected: {addr}")
        self.peer_manager.record_connection(addr, f"Device-{addr[:8]}", 'connected')
    
    def on_peer_disconnected(self, peer_info):
        """Callback when peer disconnects"""
        addr = peer_info['address']
        self.update_peers_list()
        self.update_network_status()
        self.log_network_message(f"❌ Disconnected: {addr}")
        self.peer_manager.record_connection(addr, f"Device-{addr[:8]}", 'disconnected')
    
    def on_data_received(self, message):
        """Callback when data is received"""
        try:
            data = message['data']
            if data['type'] == 'transaction':
                success = self.network_sync.process_received_transaction(data)
                if success:
                    self.log_network_message(f"📥 Received transaction: {data['sender']} → {data['receiver']}: {data['amount']} credits")
                    # Update balance if you're the receiver
                    if data['receiver'] == self.current_user:
                        self.balance += data['amount']
                        self.balance_label.setText(f"Balance: {self.balance} Credits")
        except Exception as e:
            self.log_network_message(f"⚠️ Error processing data: {str(e)}")
    
    def on_network_error(self, error):
        """Callback for network errors"""
        self.log_network_message(f"❌ Error: {error}")
    
    # UI Updates
    def update_peers_list(self):
        """Update connected peers list"""
        self.connected_peers_list.clear()
        peers = self.bt_manager.get_connected_peers()
        for peer in peers:
            self.connected_peers_list.addItem(peer)
    
    def update_network_status(self):
        """Update network status indicator"""
        peers = self.bt_manager.get_connected_peers()
        if peers:
            self.network_status.setText(f"Status: ✅ Connected ({len(peers)} peers)")
            self.network_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.network_status.setText("Status: ❌ Disconnected")
            self.network_status.setStyleSheet("color: red; font-weight: bold;")
    
    def log_network_message(self, message):
        """Log a message to the network messages area"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.network_messages.append(f"[{timestamp}] {message}")
    
    # Auth Methods
    def login(self):
        """Handle login"""
        username = self.username_input.text()
        if not username:
            self.wallet_status.setText("❌ Please enter a username")
            self.wallet_status.setStyleSheet("color: red;")
            return
        
        self.current_user = username
        self.wallet_status.setText(f"✅ Logged in as: {username}")
        self.wallet_status.setStyleSheet("color: green;")
        self.username_input.setReadOnly(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())
