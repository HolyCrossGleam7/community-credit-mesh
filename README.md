Community Credit Mesh - Desktop Application

💻 Desktop GUI for peer-to-peer mutual credit system using Python and PyQt6.
✨ Features

✅ Graphical User Interface - Easy-to-use desktop application ✅ Wallet Management - Create and manage digital wallets ✅ Peer-to-Peer Transactions - Send and receive credits directly ✅ Transaction Ledger - View complete transaction history ✅ Common Fund - Contribute to and share community funds ✅ Time Banking - Track time-based contributions ✅ Local Storage - All data stored on your device ✅ No Server Required - Completely decentralized ✅ Open Source - GPLv3 license
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

## 🔑 Digital ID & Signed Transactions

Each user is automatically assigned a **Digital ID** — a unique cryptographic
signing key (Ed25519) that is generated when you first log in and stored
privately on your device.

### How it works

1. **Login with password** — On first use your account is created and your
   password is stored as a secure hash (never in plain text).  On subsequent
   logins the password is verified; access is denied if it does not match.

2. **Every transaction is signed** — When you send credits, the transaction
   packet is signed with your private key.  Recipients can verify that the
   packet really came from you and was not tampered with.

3. **Trust-on-first-use (TOFU)** — The first time you receive a message from a
   username, their public key is *pinned* locally.  Future messages from the
   same username must use the same key.  If they differ, the transaction is
   **blocked** and an error is shown in the Status tab.

### Why this matters

Without signed transactions a malicious peer could forge a payment claiming to
be from anyone.  Signed transactions and key-pinning ensure you only accept
credits from the person who actually has the private key for that username.

### Resetting trust (peer changed devices)

If a trusted peer reinstalls the application or uses a new device their Digital
ID changes.  You will see a "Blocked — public key mismatch" error.

To allow re-pairing:

1. Open the **Peers** tab.
2. Type the peer's username in the "Reset Trust for User" field.
3. Click **Reset Trust for User**.
4. The next message from that username will be accepted and their new key
   pinned automatically.

⚠️ Security Tips:

    Keep your device secure
    Don't share your account password
    Backup your data folder regularly
    Use strong passwords
    Don't give access to others

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
📋 How to Update It on GitHub

    Go to: https://github.com/HolyCrossGleam7/community-credit-mesh
    Click on README.md file
    Click the pencil icon (Edit this file)
    Select ALL text (Ctrl+A or Cmd+A)
    Delete it
    Paste the entire text above
    Scroll to bottom
    Click "Commit changes"
    Leave message as default
    Click "Commit directly to the main branch"
    Done! ✅
