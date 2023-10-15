# the Third-party Module: Cryptography is needed
try:
    from cryptography.fernet import Fernet

    available = True
except ImportError:
    available = False


