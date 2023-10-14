try:
    from cryptography.fernet import Fernet

    available = True
except ImportError:
    available = False


