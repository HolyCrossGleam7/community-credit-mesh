# user_manager.py

"""
Module for handling user authentication and login functionality.
"""

from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Example usage
if __name__ == '__main__':
    user = User('example_user', 'example_password')
    print(user.verify_password('example_password'))  # Should return True
    print(user.verify_password('wrong_password'))  # Should return False
