from models.base import AutoParts


class User(AutoParts):
    """Represents a system user"""

    def __init__(self, id=None, username="", password=""):
        super().__init__()
        self.id = id
        self.username = username
        self.password = password

    def authenticate(self, input_username, input_password):
        """Authenticate user credentials"""
        return self.username == input_username and self.password == input_password
