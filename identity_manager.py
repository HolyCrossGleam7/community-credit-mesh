"""
identity_manager.py

Handles user authentication (password hashing), per-user Ed25519 signing
keypairs, and strict public-key trust/pinning for incoming transactions.

All security-related data is stored in the data/ folder:
  data/users.json  – username → password hash
  data/keys.json   – username → private + public key PEM  (local only!)
  data/trust.json  – username → pinned public key PEM (known peers)
"""

import base64
import hashlib
import json
import os

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from werkzeug.security import check_password_hash, generate_password_hash


class IdentityManager:
    """Manages user passwords, Ed25519 signing keypairs, and peer trust."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._users_file = os.path.join(data_dir, "users.json")
        self._keys_file = os.path.join(data_dir, "keys.json")
        self._trust_file = os.path.join(data_dir, "trust.json")

        self._users = self._load_json(self._users_file)
        self._keys = self._load_json(self._keys_file)
        self._trust = self._load_json(self._trust_file)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _load_json(self, filepath):
        try:
            with open(filepath, "r") as fh:
                return json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_json(self, filepath, data):
        with open(filepath, "w") as fh:
            json.dump(data, fh, indent=4)

    # ── account / password ────────────────────────────────────────────────────

    def authenticate(self, username, password):
        """
        Authenticate a user (or register on first use).

        Returns ``(ok: bool, message: str)`` where *message* is one of:
          ``"registered"``    – new account created
          ``"logged_in"``     – existing account, correct password
          ``"wrong_password"``– existing account, wrong password
        """
        if username not in self._users:
            self._users[username] = {
                "password_hash": generate_password_hash(password)
            }
            self._save_json(self._users_file, self._users)
            self._generate_keypair(username)
            return True, "registered"

        if check_password_hash(self._users[username]["password_hash"], password):
            if username not in self._keys:
                self._generate_keypair(username)
            return True, "logged_in"

        return False, "wrong_password"

    # ── keypair management ────────────────────────────────────────────────────

    def _generate_keypair(self, username):
        """Generate and persist an Ed25519 keypair for *username*."""
        private_key = Ed25519PrivateKey.generate()
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")
        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")
        self._keys[username] = {
            "private_key_pem": private_pem,
            "public_key_pem": public_pem,
        }
        self._save_json(self._keys_file, self._keys)

    def get_public_key_pem(self, username):
        """Return the PEM-encoded public key for *username*, or ``None``."""
        entry = self._keys.get(username)
        return entry.get("public_key_pem") if entry else None

    def key_fingerprint(self, public_key_pem):
        """Return a 16-character hex fingerprint for *public_key_pem*."""
        if not public_key_pem:
            return "unknown"
        return hashlib.sha256(public_key_pem.encode()).hexdigest()[:16]

    # ── signing ───────────────────────────────────────────────────────────────

    def sign_packet(self, username, canonical_bytes):
        """
        Sign *canonical_bytes* with *username*'s Ed25519 private key.

        Returns a base64-encoded signature string, or ``None`` if no key exists.
        """
        entry = self._keys.get(username)
        if not entry:
            return None
        private_key = serialization.load_pem_private_key(
            entry["private_key_pem"].encode("utf-8"), password=None
        )
        return base64.b64encode(private_key.sign(canonical_bytes)).decode("utf-8")

    # ── verification / trust pinning ──────────────────────────────────────────

    def verify_and_pin(self, sender_username, public_key_pem, canonical_bytes, signature_b64):
        """
        Verify *signature_b64* over *canonical_bytes* using *public_key_pem*,
        and enforce key-pinning for *sender_username*.

        On the first valid transaction from a username the key is remembered
        (pinned).  All subsequent transactions must use the same key; a
        different key is rejected with ``(False, error_message)``.

        Returns ``(valid: bool, message: str)``.
        """
        # Enforce pinned key
        pinned = self._trust.get(sender_username)
        if pinned is not None and pinned != public_key_pem:
            return False, (
                f"Key mismatch for '{sender_username}': transaction blocked. "
                "Use 'Reset Trust' on the Status tab if the key change is intentional."
            )

        # Verify signature
        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            public_key.verify(base64.b64decode(signature_b64), canonical_bytes)
        except InvalidSignature:
            return False, f"Invalid signature from '{sender_username}'"
        except Exception as exc:
            return False, f"Signature error from '{sender_username}': {exc}"

        # Pin on first valid use
        if pinned is None:
            self._trust[sender_username] = public_key_pem
            self._save_json(self._trust_file, self._trust)

        return True, "ok"

    # ── trust management ──────────────────────────────────────────────────────

    def get_trusted_users(self):
        """Return ``{username: fingerprint}`` for all pinned peers."""
        return {u: self.key_fingerprint(pem) for u, pem in self._trust.items()}

    def reset_trust(self, username):
        """
        Remove the pinned key for *username*.

        After reset, the next valid signed transaction from that username will
        be accepted and the new key will be re-pinned automatically.

        Returns ``True`` if a key was removed, ``False`` if none was found.
        """
        if username in self._trust:
            del self._trust[username]
            self._save_json(self._trust_file, self._trust)
            return True
        return False
