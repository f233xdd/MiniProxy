# the Third-party Module: Cryptography is needed in order to enable this file
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


class RSA:

    def __init__(self):
        self.__private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        self.__public_key = self.__private_key.public_key()
        self.__the_other_key: rsa.RSAPublicKey | None = None

    def encrypt(self, msg: bytes) -> bytes:
        return self.__the_other_key.encrypt(msg, padding=padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    def decrypt(self, msg: bytes) -> bytes:
        return self.__private_key.decrypt(msg, padding=padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    def get_public_key(self) -> bytes:
        return self.__public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def load_key(self, pem: bytes):
        self.__the_other_key = serialization.load_pem_public_key(pem)


if __name__ == "__main__":
    # test case
    crypto = RSA()

    b = crypto.get_public_key()
    crypto.load_key(b)

    data = b"Don't judge a book by its cover."
    res_1 = crypto.encrypt(data)
    res_2 = crypto.decrypt(res_1)

    print(res_1)
    print(res_2)

    data = b"Enjoy your day!"
    res_1 = crypto.encrypt(data)
    res_2 = crypto.decrypt(res_1)

    print(res_1)
    print(res_2)
