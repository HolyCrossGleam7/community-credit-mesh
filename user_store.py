"""
user_store.py

Persists user accounts (username → password hash) in a local JSON file.
On first login for a username the account is registered; on subsequent
logins the password is verified and access is denied on mismatch.
"""

import json
import os

from werkzeug.security import check_password_hash, generate_password_hash

_USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")


def _load() -> dict:
    if os.path.exists(_USERS_FILE):
        with open(_USERS_FILE, "r") as fh:
            return json.load(fh)
    return {}


def _save(data: dict) -> None:
    with open(_USERS_FILE, "w") as fh:
        json.dump(data, fh, indent=2)
    # Restrict to owner-only read/write to protect password hashes.
    os.chmod(_USERS_FILE, 0o600)


def register_or_verify(username: str, password: str) -> tuple[bool, bool, str]:
    """Register a new user or verify an existing one.

    Returns:
        (success, is_new, message)
        success  – True when access is granted
        is_new   – True when the account was just created
        message  – human-readable status string
    """
    users = _load()
    if username not in users:
        users[username] = {"password_hash": generate_password_hash(password)}
        _save(users)
        return True, True, "New account created."
    if check_password_hash(users[username]["password_hash"], password):
        return True, False, "Login successful."
    return False, False, "Incorrect password."
