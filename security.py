"""
security.py

Helpers for signing outgoing transaction packets and verifying incoming ones
using Ed25519 (via the ``cryptography`` library).

Canonical payload
-----------------
The signature covers a canonical JSON string built from the packet fields
*excluding* the ``public_key`` and ``signature`` meta-fields.  Fields are
sorted alphabetically and serialised without extra whitespace so the same
dict produces the same bytes on every platform.
"""

import base64
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _canonical(packet: dict) -> bytes:
    """Return canonical UTF-8 bytes for *packet*, ignoring security fields."""
    payload = {k: v for k, v in packet.items() if k not in ("public_key", "signature")}
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def sign_packet(packet: dict, private_key, public_key_hex: str) -> dict:
    """Add ``public_key`` and ``signature`` fields to *packet* in-place.

    Args:
        packet          – transaction dict (will be mutated and returned)
        private_key     – Ed25519PrivateKey instance
        public_key_hex  – hex-encoded raw public key bytes

    Returns:
        The same *packet* dict with the two new fields added.
    """
    sig_bytes = private_key.sign(_canonical(packet))
    packet["public_key"] = public_key_hex
    packet["signature"] = base64.b64encode(sig_bytes).decode()
    return packet


def verify_packet(packet: dict) -> tuple[bool, str]:
    """Verify the Ed25519 signature embedded in *packet*.

    Returns:
        (valid, message)
        valid   – True when the signature is present and correct
        message – description of the result (useful for error display)
    """
    pub_hex = packet.get("public_key")
    sig_b64 = packet.get("signature")

    if not pub_hex or not sig_b64:
        return False, "Packet is missing public_key or signature."

    try:
        pub_bytes = bytes.fromhex(pub_hex)
        public_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
        signature = base64.b64decode(sig_b64)
        public_key.verify(signature, _canonical(packet))
        return True, "Signature valid."
    except InvalidSignature:
        return False, "Signature verification failed — packet may be tampered."
    except Exception as exc:  # noqa: BLE001
        return False, f"Signature error: {exc}"
