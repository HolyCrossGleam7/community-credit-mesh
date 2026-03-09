"""
key_store.py

Generates and persists a per-user Ed25519 signing keypair the first time a
username logs in.  Private keys are stored as PKCS8 PEM files inside a local
`keys/` directory; the directory is created automatically on first use.
"""

import os

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
)

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")


def _key_path(username: str) -> str:
    os.makedirs(_KEYS_DIR, exist_ok=True)
    # Sanitise username so it is safe to use as a filename.
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in username)
    return os.path.join(_KEYS_DIR, f"{safe}.pem")


def get_or_create_keypair(username: str) -> tuple:
    """Return the (private_key, public_key_hex) for *username*.

    If no key exists yet, a new Ed25519 keypair is generated and the private
    key is persisted as a PEM file.

    Returns:
        private_key      – Ed25519PrivateKey instance
        public_key_hex   – hex-encoded raw public key bytes (64 hex chars)
    """
    path = _key_path(username)
    if os.path.exists(path):
        with open(path, "rb") as fh:
            private_key = load_pem_private_key(fh.read(), password=None)
    else:
        private_key = Ed25519PrivateKey.generate()
        pem = private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
        with open(path, "wb") as fh:
            fh.write(pem)
        # Restrict private key file to owner read/write only.
        os.chmod(path, 0o600)

    pub_bytes = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return private_key, pub_bytes.hex()
