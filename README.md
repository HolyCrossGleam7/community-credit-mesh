Community Credit Mesh - Desktop Application

💻 Desktop GUI for peer-to-peer mutual credit system using Python and PyQt6.
✨ Features

✅ Graphical User Interface - Easy-to-use desktop application ✅ Wallet Management - Create and manage digital wallets ✅ Peer-to-Peer Transactions - Send and receive credits directly ✅ Transaction Ledger - View complete transaction history ✅ Common Fund - Contribute to and share community funds ✅ Time Banking - Track time-based contributions ✅ Cold Wallet - Freeze credits into items and thaw back at your own price ✅ Local Storage - All data stored on your device ✅ No Server Required - Completely decentralized ✅ Open Source - GPLv3 license
🚀 Quick Start
System Requirements

    Python 3.7 or higher
    Windows, macOS, or Linux
    100 MB disk space
    No internet connection needed

Installation

    Download and Extract
    bash

    git clone https://github.com/HolyCrossGleam7/community-credit-mesh.git
    cd community-credit-mesh

    Install Dependencies
    bash

    pip install -r requirements.txt

    Run the Application
    bash

    python main.py

    Done! The GUI window will open

📖 How to Use
1. First Launch

    Run python main.py
    Create a new account (username and password)
    You start with 0 credits (earn by selling to peers)

2. Wallet Tab

    View your balance
    Check your username
    Manage your account
    See wallet information

3. Send Credits

    Click "Send" tab
    Enter recipient's username
    Enter amount to send
    Add optional description
    Click "Send Payment"
    Transaction completes instantly

4. Receive Credits

    Share your username with others
    Others send you credits
    Balance updates automatically
    Works peer-to-peer

5. Transaction History

    View all transactions
    See sent and received payments
    Check transaction details
    Track your balance changes

6. Common Fund

    Contribute credits to community fund
    Participate in fund distribution
    Track contributions
    See fund balance

7. Time Bank

    Log time contributions
    Track hours worked
    Exchange time for credits
    Manage time records

8. Cold Wallet (🧊)

    Freeze credits into items (e.g., eggs, rice, firewood)
    Items stored locally with quantity only — no price stored
    Thaw items back to credits at YOUR chosen price
    You decide the value when you thaw — it's never automatic
    View cold storage inventory and history
    Useful for storing value in physical goods

💡 How It Works
Wallet System
Code

Your Device
├── Wallet (stored locally)
│   ├── Username
│   ├── Balance
│   └── Transaction History
└── No server connection needed

P2P Transactions
Code

User A (100 credits)
  ↓ Sends 50 credits
User B (100 credits)
  
After transaction:
User A: 50 credits
User B: 150 credits

Data Storage

    All data stored in JSON files locally
    No internet required
    Private and secure
    Survives power outages

📁 Project Structure
Code

community-credit-mesh/
├── main.py                 # Application launcher
├── gui.py                  # PyQt6 GUI interface
├── user_manager.py         # User account management
├── wallet.py               # Wallet operations
├── ledger.py               # Transaction ledger
├── transaction.py          # P2P transactions
├── common_fund.py          # Community fund management
├── time_bank.py            # Time banking system
├── cold_wallet.py          # Cold wallet freeze/thaw operations
├── data_storage.py         # JSON data storage
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── LICENSE                # GPLv3 license
└── data/                  # Local data storage (created on first run)
    ├── users.json
    ├── transactions.json
    └── fund.json

🔧 Configuration
Modify Settings

Edit config.py to change:

    Starting balance (default: 0)
    Data directory location
    Window size and appearance
    Currency name and symbol

Example Config
Python

STARTING_BALANCE = 0
DATA_DIR = "data/"
CURRENCY_NAME = "Credits"
CURRENCY_SYMBOL = "CC"

🔒 Security & Privacy

✅ No Server - Your data never leaves your device ✅ No Tracking - No analytics or telemetry ✅ No Ads - Completely ad-free ✅ Open Source - Full transparency ✅ Local Storage - All data on your machine

🔐 Digital ID – How It Works

Every user in Community Credit Mesh has a **Digital ID**: a unique cryptographic key pair generated automatically when you first log in.  Think of it as a personal seal — like a wax stamp that only you possess.

When you send a transaction, the app uses your private key to attach an unforgeable **digital signature** to the packet.  Receiving devices verify that signature before applying the transaction.  This means:

- Nobody can pretend to be you and send transactions in your name.
- Transactions that were tampered with in transit are automatically rejected.

🔑 Strict Identity Pinning (Blocking)

The first time a transaction arrives from a given username, the sender's public key is **pinned** (remembered).  Every later transaction from that username must carry the same key.  If the key does not match, the transaction is **blocked** and an error is shown in the Status tab — no credits change hands.

This prevents attackers from hijacking an existing username with a different key.

🔓 Reset Trust (Status Tab)

If a peer genuinely replaced their key (new device, reinstall, etc.) you can **Reset Trust** for that username on the **Status tab**.  After the reset, the next valid signed transaction from that username will be accepted and its new key will be automatically re-pinned.

⚠️ Security Tips:

    Keep your device secure
    Don't share your account password
    Backup your data folder regularly (especially data/keys.json)
    Use strong passwords
    Don't give access to others

## 🧊 Cold Wallet — How It Works

The Cold Wallet lets you convert credits into **items** (freeze) and convert items back into **credits** (thaw) at a price **you set manually**.

### Freeze (Credits → Items)
- Enter an item name (e.g., "eggs", "rice", "firewood")
- Enter a quantity and the credits you want to spend
- Credits are deducted from your wallet
- Items are added to your cold storage (only name + quantity stored — **no price is saved**)

### Thaw (Items → Credits)
- Select an item from your cold storage
- Enter the quantity to thaw
- **You manually type the price per unit** — this is never automatic
- Total credits = quantity × your price
- Credits are added back to your wallet

### Why no stored price?
In a mutual credit community, the value of goods changes over time. The Cold Wallet deliberately does NOT store prices — **you decide what your items are worth when you thaw them**. This keeps the system flexible and community-driven.

### Example
1. Alice freezes 10 eggs for 5.00 credits (0.50/egg at freeze time)
2. Later, eggs are more scarce
3. Alice thaws 5 eggs at 1.00/egg (her choice) → receives 5.00 credits
4. She still has 5 eggs in cold storage

🐛 Troubleshooting
Problem: "Python not found"

Solution:

    Install Python from https://www.python.org
    Make sure to check "Add Python to PATH" during installation
    Restart your computer

Problem: "Module not found (PyQt6)"

Solution:
bash

pip install --upgrade pip
pip install -r requirements.txt

Problem: "Permission denied"

Solution (macOS/Linux):
bash

chmod +x main.py
python main.py

Problem: Data lost

Solution:

    Check data/ folder exists
    Restore from backup if available
    Create new account to start fresh

📦 Dependencies

All dependencies in requirements.txt:
Code

PyQt6==6.5.1          # GUI framework
werkzeug==2.3.6       # Security utilities
cryptography==41.0.0  # Encryption (optional)
pytest==7.4.0         # Testing

Install with:
bash

pip install -r requirements.txt

📱 Mobile Version

For mobile and web browsers, use the PWA version:

    Live App: https://HolyCrossGleam7.github.io/community-credit-mesh-pwa/
    Repository: https://github.com/HolyCrossGleam7/community-credit-mesh-pwa

📡 LoRa Version

For offline LoRa mesh networking on ESP32 hardware:

    Repository: https://github.com/HolyCrossGleam7/community-credit-mesh-lora

Both apps work peer-to-peer and independently!
🔄 Data Backup
Backup Your Data
bash

# Copy the data folder
cp -r data/ data_backup/

Restore from Backup
bash

# Restore the backup
cp -r data_backup/* data/

📚 Documentation

    PWA Version Docs - Mobile web app
    Main Project - Desktop app

🆘 Support

    🐛 Report Bugs: GitHub Issues
    💬 Discussions: GitHub Discussions
    📖 Documentation: This README

📄 License

GNU General Public License v3 (GPLv3)

See LICENSE for full details.
🌟 Features in Detail
Wallet Management

    Create and manage wallets
    Track balances in real-time
    View account information
    Manage account settings

Transactions

    Send credits to anyone
    Receive from peers
    Add descriptions
    View full history
    No transaction fees

Ledger

    Complete transaction log
    View balance changes
    Audit trail
    Transaction details

Common Fund

    Community pool
    Contribute anytime
    Transparent accounting
    Track contributions

Time Bank

    Log volunteer hours
    Convert time to credits
    Track contributions
    Community rewards

Cold Wallet

    Freeze credits into physical items
    Thaw items back to credits at manual price
    No stored price — you set value at thaw time
    Track cold storage inventory
    Full freeze/thaw history

💚 Built for Community

This software is designed to:

    Empower local communities
    Enable mutual aid
    Support time banking
    Promote economic justice
    Enable currency-free exchange

🚀 Get Started Now
bash

# 1. Clone the repository
git clone https://github.com/HolyCrossGleam7/community-credit-mesh.git

# 2. Install dependencies
cd community-credit-mesh
pip install -r requirements.txt

# 3. Run the application
python main.py

# 4. Create your account and start!

Community Credit Mesh Desktop - Empowering Communities 💚

License: GPLv3 Status: Production Ready
