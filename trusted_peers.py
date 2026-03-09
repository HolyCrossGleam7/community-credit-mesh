"""
trusted_peers.py

Implements trust-on-first-use (TOFU) public-key pinning for remote peers.

The first time a message is received from a username, their public key is
pinned locally.  On subsequent messages from the same username the key must
match the pinned value; if it differs the message is blocked.

Pinned keys are persisted in ``trusted_peers.json`` next to this file.
A user can call :func:`reset_trust` to remove the pin and re-trust the
next key seen from that username (needed when a peer reinstalls or changes
devices).
"""

import json
import os

_TRUSTED_FILE = os.path.join(os.path.dirname(__file__), "trusted_peers.json")


def _load() -> dict:
    if os.path.exists(_TRUSTED_FILE):
        with open(_TRUSTED_FILE, "r") as fh:
            return json.load(fh)
    return {}


def _save(data: dict) -> None:
    with open(_TRUSTED_FILE, "w") as fh:
        json.dump(data, fh, indent=2)
    # Restrict permissions to prevent tampering by other system users.
    os.chmod(_TRUSTED_FILE, 0o600)


def get_trusted_key(username: str) -> str | None:
    """Return the pinned public-key hex for *username*, or ``None``."""
    return _load().get(username)


def pin_key(username: str, public_key_hex: str) -> None:
    """Pin *public_key_hex* as the trusted key for *username*."""
    data = _load()
    data[username] = public_key_hex
    _save(data)


def reset_trust(username: str) -> bool:
    """Remove the pinned key for *username*.

    Returns ``True`` if a key was removed, ``False`` if there was nothing to remove.
    """
    data = _load()
    if username in data:
        del data[username]
        _save(data)
        return True
    return False


def get_all_trusted() -> dict:
    """Return a copy of all pinned {username: public_key_hex} entries."""
    return _load()
