from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class SshKey:
    def __init__(self, ssh_key_path):
        with open(ssh_key_path, 'rb') as f:
            ssh_key_data = f.read()
        self.key_data = serialization.load_pem_private_key(ssh_key_data, password=None, backend=default_backend())

    def private_key(self, encoding=None, format_=None):
        return self.key_data.private_bytes(
            encoding=encoding or serialization.Encoding.PEM,
            format=format_ or serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()).decode('utf-8')

    def public_key(self, encoding=None, format_=None):
        return self.key_data.public_key().public_bytes(encoding=encoding or serialization.Encoding.OpenSSH, format=format_ or serialization.PublicFormat.OpenSSH)
