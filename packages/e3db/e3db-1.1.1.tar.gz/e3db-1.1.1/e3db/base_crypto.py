import base64


class BaseCrypto:

    @classmethod
    def get_mode(self):
        pass

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        pass

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        pass

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        pass

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        pass

    @classmethod
    def decode_public_key(self, key):
        pass

    @classmethod
    def encode_public_key(self, key):
        pass

    @classmethod
    def decode_private_key(self, key):
        pass

    @classmethod
    def encode_private_key(self, key):
        pass

    @classmethod
    def random_key(self):
        pass

    @classmethod
    def random_nonce(self):
        pass

    @classmethod
    def generate_keypair(self):
        # return public, private
        pass

    @classmethod
    def base64decode(self, s):
        # From https://stackoverflow.com/a/9956217
        # Python base64 implementation requires padding, which may not be present in the
        # encoded public/private keypair
        return base64.urlsafe_b64decode(str(s) + '=' * (4 - len(s) % 4))

    @classmethod
    def base64encode(self, s):
        # remove "=" padding for general SDK compatibility
        return base64.urlsafe_b64encode(str(s)).strip("=")
