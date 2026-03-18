# Security Review — Community Credit Mesh

This document records the security review findings and recommendations for:

- **Desktop application** — `community-credit-mesh` (this repository, Python / PyQt6)
- **Mobile PWA** — `community-credit-mesh-pwa` ([GitHub](https://github.com/HolyCrossGleam7/community-credit-mesh-pwa) · [Live](https://HolyCrossGleam7.github.io/community-credit-mesh-pwa/))

The review is updated monthly by the [Scheduled Security Review workflow](.github/workflows/security-review.yml).  
For the vulnerability disclosure process see [.github/SECURITY.md](.github/SECURITY.md).

---

## Table of Contents

1. [Current Security Practices](#1-current-security-practices)
2. [Identified Gaps](#2-identified-gaps)
3. [Recommendations](#3-recommendations)
4. [PWA-Specific Findings](#4-pwa-specific-findings)
5. [Review History](#5-review-history)

---

## 1. Current Security Practices

### 1.1 Desktop Application

| Area | Practice | Status |
|------|----------|--------|
| Password storage | `werkzeug.security.generate_password_hash` / `check_password_hash` (PBKDF2-SHA256); scrypt available in werkzeug ≥ 2.0 as a stronger alternative | ✅ Good |
| Transaction IDs | SHA-256 hash of sender + receiver + amount + timestamp | ✅ Good |
| Data locality | All data stored on the user's device (`data/*.json`) — no cloud sync | ✅ Good |
| Open source | GPLv3 licence — full code transparency | ✅ Good |
| Dependency pinning | `requirements.txt` pins exact versions | ✅ Good |

### 1.2 Mobile PWA

| Area | Practice | Status |
|------|----------|--------|
| Served over HTTPS | GitHub Pages enforces HTTPS | ✅ Good |
| Offline support | Service worker caches assets locally | ✅ Good |
| Open source | Same GPLv3 licence | ✅ Good |

---

## 2. Identified Gaps

### 2.1 Desktop Application

#### HIGH severity

| ID | Gap | Location |
|----|-----|----------|
| D-H1 | **Authentication not enforced in the GUI** — `login()` in `gui.py` only checks that a username string is non-empty; no password is collected or verified against `user_manager.py` | `gui.py:524-543` |
| D-H2 | **Hardcoded credentials in `config.py`** — `DB_PASSWORD = 'password'` and `API_KEY = 'your_api_key'` are committed to the repository | `config.py:7,11` |
| D-H3 | **Unencrypted network transport** — WiFi peer communication uses a plain TCP socket (`socket.SOCK_STREAM`) with raw JSON; no TLS/SSL is applied | `network/wifi_server.py`, `network/wifi_client.py` |

#### MEDIUM severity

| ID | Gap | Location |
|----|-----|----------|
| D-M1 | **Data at rest is unencrypted** — `users.json`, `transactions.json`, and `fund.json` are stored as plaintext; a local attacker can read or tamper with balances and passwords | `data_storage.py` |
| D-M2 | **No session timeout** — once logged in, the session never expires regardless of inactivity | `gui.py` |
| D-M3 | **No rate limiting on transactions** — a compromised or malicious peer can flood the local ledger with transactions | `transaction.py`, `network/transaction_broadcaster.py` |
| D-M4 | **No message integrity/authentication for P2P packets** — any device on the LAN can send a crafted JSON packet to the WiFi server and it will be accepted without signature verification | `network/wifi_server.py:76-84` |
| D-M5 | **No 2FA support** — there is no second authentication factor for high-value operations (large transfers, fund distributions) | `user_manager.py` |

#### LOW severity

| ID | Gap | Location |
|----|-----|----------|
| D-L1 | **No input sanitisation on transaction descriptions** — free-text `description` fields are stored and displayed without sanitisation | `transaction.py:5`, `gui.py` |
| D-L2 | **`config.py` contains database/API settings not used by the application** — misleads reviewers and may encourage copy-paste of insecure patterns | `config.py` |
| D-L3 | **Exception details silently swallowed** — several `except Exception as e: pass` blocks hide errors that could indicate active attacks | `network/wifi_server.py:85-86`, `network/wifi_client.py` |

### 2.2 Mobile PWA

| ID | Gap | Area |
|----|-----|------|
| P-H1 | **No Content Security Policy (CSP)** — without a CSP header or `<meta>` tag, the app is vulnerable to XSS if any third-party content is injected | HTML / service worker |
| P-H2 | **Browser storage is unencrypted** — `localStorage` / `IndexedDB` data is readable by any JavaScript running on the same origin (and by the OS on unencrypted devices) | Front-end storage |
| P-M1 | **No authentication mechanism documented** — it is unclear whether the PWA enforces any identity verification before allowing transactions | Authentication |
| P-M2 | **No Subresource Integrity (SRI) on external scripts/styles** — if any CDN resource is loaded without an `integrity` attribute, a supply-chain attack could execute arbitrary code | HTML |
| P-L1 | **Service worker scope and cache expiry not reviewed** — stale cached resources may prevent security patches from reaching users promptly | Service worker |

---

## 3. Recommendations

### 3.1 Desktop Application

#### High-priority fixes

**D-H1 — Enforce password authentication in the GUI**

Wire the login flow in `gui.py` to `user_manager.User.verify_password`:

```python
# gui.py — suggested change
def login(self):
    username = self.username_input.text().strip()
    password = self.password_input.text()
    user = self.user_manager.get_user(username)
    if not user or not user.verify_password(password):
        self.wallet_status.setText("❌ Invalid username or password")
        return
    self.current_user = username
    ...
```

**D-H2 — Remove hardcoded credentials from `config.py`**

Replace hardcoded values with environment-variable lookups:

```python
import os
DB_PASSWORD = os.environ.get("CCM_DB_PASSWORD", "")
API_KEY     = os.environ.get("CCM_API_KEY", "")
```

Add `config.py` secrets and any `.env` files to `.gitignore`.

**D-H3 — Encrypt WiFi peer communication (TLS)**

Wrap the server and client sockets with `ssl.wrap_socket` / `ssl.SSLContext`:

```python
import ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
self.server_socket = context.wrap_socket(
    socket.socket(socket.AF_INET, socket.SOCK_STREAM),
    server_side=True
)
```

For a local-network app, generate a self-signed CA and distribute its certificate to peer devices at pairing time.

#### Medium-priority fixes

**D-M1 — Encrypt data at rest**

Use the `cryptography` library (already in `requirements.txt`) to encrypt `data/*.json` with a key derived from the user's password (Fernet + PBKDF2):

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
```

**D-M2 — Add session timeout**

Start a `QTimer` on login and call `logout()` after a configurable idle period (default: 15 minutes).

**D-M4 — Sign P2P transaction packets**

Add an HMAC-SHA256 signature to every broadcast packet, keyed to a shared secret established during device pairing:

```python
import hmac, hashlib
sig = hmac.new(shared_key, payload_bytes, hashlib.sha256).hexdigest()
packet["sig"] = sig
```

**D-M5 — Offer TOTP-based 2FA**

Use `pyotp` to generate TOTP secrets per user. Prompt for a 6-digit code on login or before any transaction above a configurable threshold.

#### Low-priority fixes

**D-L1** — Sanitise transaction `description` fields (strip control characters, enforce max length).

**D-L2** — Remove or clearly comment the unused database/API settings in `config.py`.

**D-L3** — Replace silent `except: pass` with structured logging so anomalies are visible.

### 3.2 Mobile PWA

**P-H1 — Add a Content Security Policy**

In the PWA's HTML `<head>` or via a server-side header:

```html
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; object-src 'none';">
```

**P-H2 — Encrypt sensitive browser storage**

Use the Web Crypto API (`SubtleCrypto`) to encrypt wallet data before writing to `localStorage` / `IndexedDB`:

```js
const key = await crypto.subtle.deriveKey(
  { name: 'PBKDF2', salt, iterations: 600_000, hash: 'SHA-256' },
  baseKey,
  { name: 'AES-GCM', length: 256 },
  false,
  ['encrypt', 'decrypt']
);
```

**P-M1 — Document and enforce authentication before any transaction**

Ensure the PWA requires a PIN/passphrase before allowing balance changes or transaction sends.

**P-M2 — Add SRI attributes to any externally loaded resources**

```html
<script src="https://cdn.example.com/lib.js"
        integrity="sha384-<hash>"
        crossorigin="anonymous"></script>
```

**P-L1 — Review service worker cache strategy**

Use a `stale-while-revalidate` or `network-first` strategy for application logic files so that security patches reach users within one page load.

---

## 4. PWA-Specific Findings

The PWA repository (`community-credit-mesh-pwa`) was reviewed at the level of published documentation and the live GitHub Pages deployment. A full source-code audit of that repository should be conducted separately and linked here once complete.

Key areas to audit in the PWA codebase:

1. Service worker (`sw.js`) — cache scope, update lifecycle, fetch interception
2. Manifest (`manifest.json`) — no sensitive data embedded
3. Storage layer — what data is persisted and in what format
4. Network calls — any external API endpoints or CDN resources
5. Authentication — how user identity is established and maintained across sessions

---

## 5. Review History

| Date | Reviewer | Summary |
|------|----------|---------|
| 2026-03-09 | Initial automated review | Baseline findings documented; 3 HIGH, 5 MEDIUM, 3 LOW gaps for desktop; 2 HIGH, 2 MEDIUM, 1 LOW gaps for PWA |

_This table is updated each time the monthly security review produces new findings._
