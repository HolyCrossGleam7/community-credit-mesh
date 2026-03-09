import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, 
                              QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QListWidget, 
                              QListWidgetItem, QTextEdit, QComboBox, QCheckBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from datetime import datetime
from network.network_manager import NetworkManager
from network.network_sync import NetworkSync
from network.transaction_broadcaster import TransactionBroadcaster
from peer_manager import PeerManager
from debt_tracker import DebtTracker
from identity_manager import IdentityManager


def _canonical_bytes(packet):
    """Return a deterministic bytes representation of the core transaction fields."""
    return (
        f"{packet['sender']}|{packet['receiver']}|"
        f"{float(packet['amount']):.8f}|{packet['timestamp']}|"
        f"{packet['transaction_id']}"
    ).encode("utf-8")


class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Community Credit Mesh - Desktop (Phase 1 & 2)')
        self.setGeometry(100, 100, 900, 700)
        
        # Initialize unified network manager (handles both Bluetooth and WiFi)
        self.network_manager = NetworkManager("My-CCM-Device")
        self.network_sync = NetworkSync()
        self.broadcaster = TransactionBroadcaster(self.network_sync, self.network_manager)
        self.peer_manager = PeerManager()
        
        # Set up callbacks
        self.network_manager.set_callback('on_data_received', self.on_data_received)
        self.network_manager.set_callback('on_error', self.on_network_error)
        
        self.current_user = None
        self.balance = 0
        self.server_running = False
        self.wifi_mode = 'server'  # server or client
        self.debt_tracker = DebtTracker()
        self.identity_manager = IdentityManager()
        
        self.initUI()
        
        # Auto-broadcast presence every 5 seconds
        self.broadcast_timer = QTimer()
        self.broadcast_timer.timeout.connect(self.broadcast_wifi_presence)
        self.broadcast_timer.start(5000)
    
    def initUI(self):
        """Initialize the user interface"""
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Create tabs
        self.wallet_tab = self.create_wallet_tab()
        self.send_tab = self.create_send_tab()
        self.bluetooth_tab = self.create_bluetooth_tab()
        self.wifi_tab = self.create_wifi_tab()
        self.peers_tab = self.create_peers_tab()
        self.status_tab = self.create_status_tab()
        
        # Add tabs
        self.tabs.addTab(self.wallet_tab, "💳 Wallet")
        self.tabs.addTab(self.send_tab, "📤 Send")
        self.tabs.addTab(self.bluetooth_tab, "🔵 Bluetooth")
        self.tabs.addTab(self.wifi_tab, "🌐 WiFi")
        self.tabs.addTab(self.peers_tab, "👥 Peers")
        self.tabs.addTab(self.status_tab, "📊 Status")
    
    def create_wallet_tab(self):
        """Create Wallet tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("💳 Community Credit Mesh Wallet"))
        
        self.wallet_status = QLabel(f"Status: Not logged in")
        layout.addWidget(self.wallet_status)
        
        self.balance_label = QLabel("")
        self.balance_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.balance_label)
        
        self.debt_warning_label = QLabel("")
        self.debt_warning_label.setWordWrap(True)
        layout.addWidget(self.debt_warning_label)
        
        self.update_balance_display()
        
        # Login section
        login_layout = QHBoxLayout()
        login_layout.addWidget(QLabel("Username:"))
        self.username_input = QLineEdit()
        login_layout.addWidget(self.username_input)

        login_layout.addWidget(QLabel("Password:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password")
        login_layout.addWidget(self.password_input)
        
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
        
        layout.addWidget(QLabel("📤 Send Credits"))
        
        layout.addWidget(QLabel("Recipient:"))
        self.recipient_input = QLineEdit()
        layout.addWidget(self.recipient_input)
        
        layout.addWidget(QLabel("Amount:"))
        self.amount_input = QLineEdit()
        layout.addWidget(self.amount_input)
        
        layout.addWidget(QLabel("Description:"))
        self.description_input = QLineEdit()
        layout.addWidget(self.description_input)
        
        send_btn = QPushButton("📤 Send & Broadcast")
        send_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        send_btn.clicked.connect(self.send_credits)
        layout.addWidget(send_btn)
        
        self.send_debt_warning_label = QLabel("")
        self.send_debt_warning_label.setWordWrap(True)
        layout.addWidget(self.send_debt_warning_label)
        
        self.send_status = QLabel("")
        layout.addWidget(self.send_status)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_bluetooth_tab(self):
        """Create Bluetooth tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🔵 Bluetooth Network"))
        
        self.bt_status = QLabel("Status: ❌ Disconnected")
        self.bt_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.bt_status)
        
        # Server control
        server_layout = QHBoxLayout()
        self.bt_server_btn = QPushButton("▶ Start Bluetooth Server")
        self.bt_server_btn.clicked.connect(self.toggle_bt_server)
        self.bt_server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        server_layout.addWidget(self.bt_server_btn)
        
        bt_scan_btn = QPushButton("🔍 Scan Devices")
        bt_scan_btn.clicked.connect(self.scan_bt_devices)
        bt_scan_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        server_layout.addWidget(bt_scan_btn)
        
        layout.addLayout(server_layout)
        
        layout.addWidget(QLabel("Available Bluetooth Devices:"))
        self.bt_device_list = QListWidget()
        layout.addWidget(self.bt_device_list)
        
        bt_connect_btn = QPushButton("🔗 Connect Selected")
        bt_connect_btn.clicked.connect(self.connect_bt_device)
        bt_connect_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(bt_connect_btn)
        
        layout.addWidget(QLabel("Connected Bluetooth Peers:"))
        self.bt_peers_list = QListWidget()
        layout.addWidget(self.bt_peers_list)
        
        bt_disconnect_btn = QPushButton("❌ Disconnect")
        bt_disconnect_btn.clicked.connect(self.disconnect_bt_device)
        bt_disconnect_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        layout.addWidget(bt_disconnect_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_wifi_tab(self):
        """Create WiFi tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("🌐 WiFi Network"))
        
        self.wifi_status = QLabel("Status: ❌ Not running")
        self.wifi_status.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.wifi_status)
        
        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("WiFi Mode:"))
        
        self.wifi_mode_combo = QComboBox()
        self.wifi_mode_combo.addItems(["📡 Server (receive connections)", "🔌 Client (connect to server)"])
        mode_layout.addWidget(self.wifi_mode_combo)
        
        layout.addLayout(mode_layout)
        
        # Server mode
        layout.addWidget(QLabel("Server Mode:"))
        wifi_server_layout = QHBoxLayout()
        
        self.wifi_server_btn = QPushButton("▶ Start WiFi Server")
        self.wifi_server_btn.clicked.connect(self.toggle_wifi_server)
        self.wifi_server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
        wifi_server_layout.addWidget(self.wifi_server_btn)
        
        wifi_discover_btn = QPushButton("🔍 Start Discovery")
        wifi_discover_btn.clicked.connect(self.start_wifi_discovery)
        wifi_discover_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        wifi_server_layout.addWidget(wifi_discover_btn)
        
        layout.addLayout(wifi_server_layout)
        
        layout.addWidget(QLabel("Discovered WiFi Devices:"))
        self.wifi_device_list = QListWidget()
        layout.addWidget(self.wifi_device_list)
        
        # Client mode
        layout.addWidget(QLabel("Client Mode:"))
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Server IP:"))
        self.server_ip_input = QLineEdit()
        self.server_ip_input.setPlaceholderText("192.168.1.100")
        client_layout.addWidget(self.server_ip_input)
        
        wifi_connect_btn = QPushButton("🔗 Connect to Server")
        wifi_connect_btn.clicked.connect(self.connect_wifi_server)
        wifi_connect_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        client_layout.addWidget(wifi_connect_btn)
        
        layout.addLayout(client_layout)
        
        layout.addWidget(QLabel("Connected WiFi Clients:"))
        self.wifi_clients_list = QListWidget()
        layout.addWidget(self.wifi_clients_list)
        
        wifi_disconnect_btn = QPushButton("❌ Disconnect All WiFi")
        wifi_disconnect_btn.clicked.connect(self.disconnect_wifi_all)
        wifi_disconnect_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        layout.addWidget(wifi_disconnect_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_peers_tab(self):
        """Create Peers tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("👥 Connected Peers Management"))
        
        layout.addWidget(QLabel("All Peers:"))
        self.peers_list = QListWidget()
        layout.addWidget(self.peers_list)
        
        layout.addWidget(QLabel("Peer Details:"))
        self.peer_details = QTextEdit()
        self.peer_details.setReadOnly(True)
        self.peer_details.setMaximumHeight(200)
        layout.addWidget(self.peer_details)
        
        button_layout = QHBoxLayout()
        
        fav_btn = QPushButton("⭐ Mark as Favorite")
        fav_btn.clicked.connect(self.mark_favorite)
        button_layout.addWidget(fav_btn)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_peers)
        button_layout.addWidget(refresh_btn)
        
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_status_tab(self):
        """Create Status tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("📊 Network Status & Messages"))
        
        self.status_display = QTextEdit()
        self.status_display.setReadOnly(True)
        layout.addWidget(self.status_display)

        # ── Digital ID / Trust section ────────────────────────────────────────
        layout.addWidget(QLabel("🔐 Digital ID – Trusted Peers (pinned keys)"))

        self.trust_list = QListWidget()
        self.trust_list.setMaximumHeight(150)
        layout.addWidget(self.trust_list)

        trust_btn_layout = QHBoxLayout()
        reset_trust_btn = QPushButton("🗑 Reset Trust for Selected")
        reset_trust_btn.setStyleSheet(
            "background-color: #FF5722; color: white; padding: 6px;"
        )
        reset_trust_btn.clicked.connect(self.reset_selected_trust)
        trust_btn_layout.addWidget(reset_trust_btn)

        refresh_trust_btn = QPushButton("🔄 Refresh")
        refresh_trust_btn.clicked.connect(self.refresh_trust_list)
        trust_btn_layout.addWidget(refresh_trust_btn)

        layout.addLayout(trust_btn_layout)
        
        widget.setLayout(layout)
        return widget
    
    # Bluetooth Methods
    def toggle_bt_server(self):
        """Start/Stop Bluetooth server"""
        if not self.server_running:
            self.network_manager.bluetooth.start_server()
            self.server_running = True
            self.bt_server_btn.setText("⏹ Stop Bluetooth Server")
            self.bt_server_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 10px;")
            self.log_message("✅ Bluetooth server started")
        else:
            self.network_manager.bluetooth.stop_server()
            self.server_running = False
            self.bt_server_btn.setText("▶ Start Bluetooth Server")
            self.bt_server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
            self.log_message("⏹ Bluetooth server stopped")
    
    def scan_bt_devices(self):
        """Scan for Bluetooth devices"""
        self.log_message("🔍 Scanning for Bluetooth devices...")
        devices = self.network_manager.bluetooth.scan_for_devices(timeout=5)
        
        self.bt_device_list.clear()
        for addr, info in devices.items():
            item_text = f"{info['name']} ({addr})"
            self.bt_device_list.addItem(item_text)
        
        self.log_message(f"✅ Found {len(devices)} Bluetooth devices")
    
    def connect_bt_device(self):
        """Connect to Bluetooth device"""
        selected = self.bt_device_list.currentItem()
        if not selected:
            self.log_message("⚠️ Please select a device")
            return
        
        text = selected.text()
        addr = text.split('(')[1].rstrip(')')
        
        self.log_message(f"🔗 Connecting to Bluetooth {addr}...")
        success = self.network_manager.connect_bluetooth(addr)
        
        if success:
            self.log_message(f"✅ Connected via Bluetooth to {addr}")
        else:
            self.log_message(f"❌ Failed to connect")
    
    def disconnect_bt_device(self):
        """Disconnect Bluetooth device"""
        selected = self.bt_peers_list.currentItem()
        if not selected:
            self.log_message("⚠️ Please select a peer")
            return
        
        peer = selected.text()
        self.network_manager.disconnect_all()
        self.log_message(f"✅ Disconnected")
        self.update_connection_status()
    
    # WiFi Methods
    def toggle_wifi_server(self):
        """Start/Stop WiFi server"""
        if self.network_manager.wifi_server.listening:
            self.network_manager.wifi_server.stop()
            self.wifi_server_btn.setText("▶ Start WiFi Server")
            self.wifi_server_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 10px;")
            self.log_message("⏹ WiFi server stopped")
        else:
            self.network_manager.wifi_server.start()
            ip = self.network_manager.wifi_discovery.get_local_ip()
            self.wifi_server_btn.setText("⏹ Stop WiFi Server")
            self.wifi_server_btn.setStyleSheet("background-color: #FF5722; color: white; padding: 10px;")
            self.log_message(f"✅ WiFi server started at {ip}:5556")
    
    def start_wifi_discovery(self):
        """Start WiFi device discovery"""
        self.log_message("🔍 Starting WiFi discovery...")
        self.network_manager.wifi_discovery.start_discovery()
        self.log_message("✅ WiFi discovery started (broadcasting presence every 5 seconds)")
    
    def broadcast_wifi_presence(self):
        """Broadcast WiFi presence"""
        self.network_manager.wifi_discovery.broadcast_presence()
    
    def connect_wifi_server(self):
        """Connect to WiFi server"""
        server_ip = self.server_ip_input.text()
        if not server_ip:
            self.log_message("⚠️ Please enter server IP")
            return
        
        self.log_message(f"🔗 Connecting to WiFi server at {server_ip}...")
        success = self.network_manager.connect_wifi(server_ip)
        
        if success:
            self.log_message(f"✅ Connected to WiFi server at {server_ip}")
        else:
            self.log_message(f"❌ Failed to connect to WiFi server")
        
        self.update_connection_status()
    
    def disconnect_wifi_all(self):
        """Disconnect all WiFi connections"""
        self.network_manager.wifi_server.disconnect_all()
        self.network_manager.wifi_client.disconnect()
        self.log_message("✅ All WiFi connections closed")
        self.update_connection_status()
    
    # Transaction Methods
    def send_credits(self):
        """Send credits with broadcast"""
        if not self.current_user:
            self.send_status.setText("❌ Please login first")
            self.send_status.setStyleSheet("color: red;")
            return
        
        if self.debt_tracker.is_in_debt(self.current_user):
            self.send_status.setText("❌ Cannot send credits while a debt is active. Please repay your debt first.")
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
            
            self.balance -= amount
            
            if self.balance < 0:
                self.debt_tracker.record_debt(self.current_user, abs(self.balance))
            
            # Build packet then sign it
            packet = self.network_sync.create_transaction_packet(
                self.current_user, recipient, amount, description
            )
            canonical = _canonical_bytes(packet)
            pub_key_pem = self.identity_manager.get_public_key_pem(self.current_user)
            signature = self.identity_manager.sign_packet(self.current_user, canonical)
            if not pub_key_pem or not signature:
                self.send_status.setText("❌ Digital ID not available – please log in again")
                self.send_status.setStyleSheet("color: red;")
                return
            packet['sender_public_key'] = pub_key_pem
            packet['signature'] = signature

            result = self.broadcaster.broadcast_packet(packet)
            
            total_peers = result.get('peers_notified', 0)
            self.send_status.setText(f"✅ Sent {amount} to {recipient} ({total_peers} peers notified)")
            self.send_status.setStyleSheet("color: green;")
            
            self.recipient_input.clear()
            self.amount_input.clear()
            self.description_input.clear()
            
            self.log_message(f"📤 Transaction broadcast: {self.current_user} → {recipient}: {amount} credits")
            self.update_balance_display()
            self.update_debt_warnings()
        except ValueError:
            self.send_status.setText("❌ Invalid amount")
            self.send_status.setStyleSheet("color: red;")
    
    # Peer Management
    def refresh_peers(self):
        """Refresh peers list"""
        self.peers_list.clear()
        peers = self.peer_manager.get_all_peers()
        
        for addr, info in peers.items():
            favorite = "⭐" if info.get('favorite') else "  "
            item_text = f"{favorite} {info['name']} ({addr})"
            self.peers_list.addItem(item_text)
    
    def mark_favorite(self):
        """Mark peer as favorite"""
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
    def on_data_received(self, message):
        """Handle received data"""
        try:
            data = message['data']
            if data['type'] == 'transaction':
                # Verify digital signature before processing
                pub_key = data.get('sender_public_key')
                sig = data.get('signature')
                if not pub_key or not sig:
                    self.log_message(
                        f"🚫 Unsigned transaction from '{data.get('sender', '?')}' rejected"
                    )
                    return
                canonical = _canonical_bytes(data)
                valid, reason = self.identity_manager.verify_and_pin(
                    data['sender'], pub_key, canonical, sig
                )
                if not valid:
                    self.log_message(f"🚫 {reason}")
                    self.refresh_trust_list()
                    return

                success = self.network_sync.process_received_transaction(data)
                if success:
                    self.log_message(f"📥 Transaction: {data['sender']} → {data['receiver']}: {data['amount']}")
                    if data['receiver'] == self.current_user:
                        self.balance += data['amount']
                        if self.balance >= 0 and self.debt_tracker.is_in_debt(self.current_user):
                            self.debt_tracker.clear_debt(self.current_user)
                            self.log_message("✅ Debt cleared — balance restored to non-negative")
                        self.update_balance_display()
                        self.update_debt_warnings()
                    self.refresh_trust_list()
        except Exception as e:
            self.log_message(f"⚠️ Error: {str(e)}")
    
    def on_network_error(self, error):
        """Handle network errors"""
        self.log_message(f"❌ Error: {error}")
    
    # UI Updates
    def update_connection_status(self):
        """Update connection status"""
        status = self.network_manager.get_connection_status()
        
        total = status['total_connections']
        if total > 0:
            self.bt_status.setText(f"✅ Connected ({total} connections)")
            self.bt_status.setStyleSheet("color: green; font-weight: bold;")
            self.wifi_status.setText(f"✅ Connected ({total} connections)")
            self.wifi_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.bt_status.setText("Status: ❌ Disconnected")
            self.bt_status.setStyleSheet("color: red; font-weight: bold;")
            self.wifi_status.setText("Status: ❌ Not running")
            self.wifi_status.setStyleSheet("color: red; font-weight: bold;")
    
    def log_message(self, message):
        """Log message to status tab"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.status_display.append(f"[{timestamp}] {message}")
    
    def login(self):
        """Handle login – registers on first use, verifies password on return."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username:
            self.wallet_status.setText("❌ Please enter a username")
            self.wallet_status.setStyleSheet("color: red;")
            return
        if not password:
            self.wallet_status.setText("❌ Please enter a password")
            self.wallet_status.setStyleSheet("color: red;")
            return
        
        ok, msg = self.identity_manager.authenticate(username, password)
        if not ok:
            self.wallet_status.setText("❌ Wrong password – access denied")
            self.wallet_status.setStyleSheet("color: red;")
            self.log_message(f"🚫 Failed login attempt for '{username}'")
            return

        self.current_user = username
        if msg == "registered":
            self.wallet_status.setText(f"✅ New account created & logged in as: {username}")
            self.log_message(f"👤 New user '{username}' registered and logged in")
        else:
            self.wallet_status.setText(f"✅ Logged in as: {username}")
            self.log_message(f"👤 User '{username}' logged in")

        pub_key = self.identity_manager.get_public_key_pem(username)
        fingerprint = self.identity_manager.key_fingerprint(pub_key) if pub_key else "N/A"
        self.log_message(f"🔑 Digital ID fingerprint: {fingerprint}")

        self.wallet_status.setStyleSheet("color: green;")
        self.username_input.setReadOnly(True)
        self.password_input.setReadOnly(True)
        
        debt_status = self.debt_tracker.get_debt_status(username)
        if debt_status['has_debt']:
            if debt_status['status'] == 'overdue':
                self.log_message(f"🚨 DEBT OVERDUE by {debt_status['overdue_by']} days! Amount: {debt_status['amount']} credits")
            elif debt_status['status'] == 'due_today':
                self.log_message(f"⚠️ Debt due TODAY! Amount: {debt_status['amount']} credits")
            else:
                days = debt_status['days_remaining']
                day_word = 'day' if days == 1 else 'days'
                self.log_message(f"⏳ Active debt: {debt_status['amount']} credits — {days} {day_word} remaining to repay")
        else:
            self.log_message("✅ No active debt")
        
        self.update_debt_warnings()
        self.refresh_trust_list()
    
    def update_debt_warnings(self):
        """Update debt warning labels in wallet and send tabs"""
        if not self.current_user:
            self.debt_warning_label.setText("")
            self.send_debt_warning_label.setText("")
            return
        
        debt_status = self.debt_tracker.get_debt_status(self.current_user)
        
        if not debt_status['has_debt']:
            self.debt_warning_label.setText("")
            self.send_debt_warning_label.setText("")
            return
        
        if debt_status['status'] == 'overdue':
            msg = f"🚨 DEBT OVERDUE by {debt_status['overdue_by']} days! Repay {debt_status['amount']} credits to resume sending."
            style = "color: #b71c1c; font-weight: bold; background-color: #ffebee; padding: 6px; border-radius: 4px;"
        elif debt_status['status'] == 'due_today':
            msg = f"⚠️ Debt of {debt_status['amount']} credits is due TODAY! Sending is blocked."
            style = "color: #e65100; font-weight: bold; background-color: #fff3e0; padding: 6px; border-radius: 4px;"
        else:
            days = debt_status['days_remaining']
            day_word = 'day' if days == 1 else 'days'
            msg = f"⏳ Active debt: {debt_status['amount']} credits — {days} {day_word} remaining to repay. Sending is blocked."
            style = "color: #f57f17; font-weight: bold; background-color: #fffde7; padding: 6px; border-radius: 4px;"
        
        self.debt_warning_label.setText(msg)
        self.debt_warning_label.setStyleSheet(style)
        self.send_debt_warning_label.setText(msg)
        self.send_debt_warning_label.setStyleSheet(style)
    
    def refresh_trust_list(self):
        """Refresh the pinned-keys list in the Status tab."""
        self.trust_list.clear()
        trusted = self.identity_manager.get_trusted_users()
        if not trusted:
            self.trust_list.addItem("(no pinned peers yet)")
        else:
            for username, fingerprint in trusted.items():
                self.trust_list.addItem(f"{username}  ·  fingerprint: {fingerprint}")

    def reset_selected_trust(self):
        """Remove the pinned key for the selected peer."""
        selected = self.trust_list.currentItem()
        if not selected:
            self.log_message("⚠️ Please select a peer to reset trust for")
            return
        text = selected.text()
        if text.startswith("("):
            return
        parts = text.split("  ·  ")
        if len(parts) < 1:
            return
        username = parts[0].strip()
        if not username:
            return
        removed = self.identity_manager.reset_trust(username)
        if removed:
            self.log_message(f"🔓 Trust reset for '{username}' — next valid signed transaction will re-pin")
        self.refresh_trust_list()

    def update_balance_display(self):
        """Update balance display with debt/credit indication"""
        if self.balance >= 0:
            text = f"💚 Credit: +{self.balance} Credits"
            color = "#4CAF50"  # Green for credit
        else:
            text = f"❌ Debt: {self.balance} Credits"
            color = "#f44336"  # Red for debt
        
        self.balance_label.setText(text)
        self.balance_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApplication()
    window.show()
    sys.exit(app.exec())
