import os
import json


class Credentials:
    """Load credentials information like passwords."""

    def __init__(
        self,
        user_name,
        password,
        email_address,
        certificates=None
    ):
        """Initialize the credentials."""
        self.user_name = user_name
        self.password = password
        self.email_address = email_address
        self.certificates = certificates

    @property
    def user_name(self):
        """Get Username."""
        return self.__user_name

    @user_name.setter
    def user_name(self, user_name):
        """Set Username."""
        self.__user_name = user_name

    @property
    def password(self):
        """Get Password."""
        return self.__password

    @password.setter
    def password(self, password):
        """Set Username."""
        self.__password = password

    @property
    def email_address(self):
        """Get Email Address."""
        return self.__email_address

    @email_address.setter
    def email_address(self, email_address):
        """Set Username."""
        self.__email_address = email_address


def from_json(f):
    """Load credentials from json."""
    with open(f) as f:
        user_secrets = json.load(f)
        creds = Credentials(
            user_name=user_secrets['user_name'],
            password=user_secrets['password'],
            email_address=user_secrets['email_address'])
        return creds


def auto():
    """Look for the secret.json file."""
    # traverse root directory looking for credentials
    for root, dirs, files in os.walk("."):
        for f in files:
            if f == 'secret.json':
                try:
                    return from_json(f)
                except(ValueError):
                    raise ValueError('Could not open {f}'.format(f=f))
                break
