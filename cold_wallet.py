# cold_wallet.py

class ColdWallet:
    def __init__(self):
        self.cold_wallets = {}  # {user_id: {item_name: quantity, ...}}

    def freeze(self, user_id, item_name, quantity):
        """Add items to cold wallet. Only stores name + qty, no price."""
        if user_id not in self.cold_wallets:
            self.cold_wallets[user_id] = {}
        if item_name in self.cold_wallets[user_id]:
            self.cold_wallets[user_id][item_name] += quantity
        else:
            self.cold_wallets[user_id][item_name] = quantity
        return True

    def thaw(self, user_id, item_name, quantity):
        """Remove items from cold wallet. Does NOT handle credits. Returns True on success, False otherwise."""
        if not self.has_item(user_id, item_name, quantity):
            return False
        self.cold_wallets[user_id][item_name] -= quantity
        if self.cold_wallets[user_id][item_name] <= 0:
            del self.cold_wallets[user_id][item_name]
        return True

    def get_cold_wallet(self, user_id):
        """Return dict of {item_name: quantity} for the user."""
        return dict(self.cold_wallets.get(user_id, {}))

    def get_item_quantity(self, user_id, item_name):
        """Return quantity of a specific item for the user."""
        return self.cold_wallets.get(user_id, {}).get(item_name, 0)

    def has_item(self, user_id, item_name, quantity):
        """Check if user has at least the given quantity of an item."""
        return self.get_item_quantity(user_id, item_name) >= quantity
