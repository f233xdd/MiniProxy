# the Third-party Module: Cryptography is needed in order to enable this file
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class RSA:

    def __init__(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.__public_key = self.__private_key.public_key()
        self.__the_other_key: rsa.RSAPublicKey | None = None

    def encrypt(self, data: bytes) -> bytes:
        return self.__the_other_key.encrypt(data, padding=padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
                                            )

    def decrypt(self, data: bytes) -> bytes:
        return self.__private_key.decrypt(data, padding=padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
                                          )

    def get_public_key(self) -> bytes:
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def load_key(self, pem: bytes):
        self.__the_other_key = serialization.load_pem_public_key(pem)


class Cipher:

    def __init__(self):
        self.__keys = [Fernet.generate_key(), b""]
        self.__encrypter = Fernet(self.__keys[0])
        self.__decipher = None

    def load_key(self, key: bytes):
        self.__decipher = Fernet(key)
        self.__keys[1] = key

    def encrypt(self, data: bytes) -> bytes:
        return self.__encrypter.encrypt(data)

    def decrypt(self, data: bytes) -> bytes:
        return self.__decipher.decrypt(data)

    @property
    def encrypt_key(self) -> bytes:
        return self.__keys[0]

    @property
    def decrypt_key(self) -> bytes:
        return self.__keys[1]


if __name__ == "__main__":
    # test case
    c1 = Cipher()
    c2 = Cipher()
    c1.load_key(c2.encrypt_key)
    c2.load_key(c1.encrypt_key)
    d = b"\x90" * 10000000
    res1 = c1.encrypt(d)
    res2 = c2.decrypt(res1)
    assert d == res2

    crypto = RSA()
    b = crypto.get_public_key()
    crypto.load_key(b)
    # 958 8192
    # 446 4096
    # 190 2048
    # 62 1024
    d = b"\x3b" * 62
    res_1 = crypto.encrypt(d)
    res_2 = crypto.decrypt(res_1)
    assert d == res_2

    d = b"Enjoy your day!"
    res_1 = crypto.encrypt(d)
    res_2 = crypto.decrypt(res_1)
    assert d == res_2

    print(len(crypto.encrypt(c1.encrypt_key)), len(crypto.encrypt(c1.decrypt_key)))
