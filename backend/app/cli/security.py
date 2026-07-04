import os
from cryptography.fernet import Fernet

DEFAULT_KEY_PATH = os.path.expanduser("~/.devlens/.key")

def get_encryption_key() -> bytes:
    """Retrieve or generate the local encryption key."""
    key_dir = os.path.dirname(DEFAULT_KEY_PATH)
    try:
        os.makedirs(key_dir, exist_ok=True)
    except Exception:
        pass
    if not os.path.exists(DEFAULT_KEY_PATH):
        key = Fernet.generate_key()
        try:
            with open(DEFAULT_KEY_PATH, "wb") as f:
                f.write(key)
        except Exception:
            return key
        return key
    try:
        with open(DEFAULT_KEY_PATH, "rb") as f:
            return f.read()
    except Exception:
        return Fernet.generate_key()

def encrypt_token(token: str) -> str:
    """Encrypt a plaintext token using Fernet and return with the 'enc:' prefix."""
    if not token:
        return ""
    if token.startswith("enc:"):
        return token
    key = get_encryption_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(token.encode("utf-8"))
    return "enc:" + encrypted.decode("utf-8")

def decrypt_token(enc_token: str) -> str:
    """Decrypt a token if it has the 'enc:' prefix, otherwise returns it as plaintext."""
    if not enc_token:
        return ""
    if not enc_token.startswith("enc:"):
        return enc_token
    actual_enc = enc_token[4:]
    key = get_encryption_key()
    fernet = Fernet(key)
    try:
        decrypted = fernet.decrypt(actual_enc.encode("utf-8"))
        return decrypted.decode("utf-8")
    except Exception:
        return ""
