import base64
import nacl.utils
import nacl.secret
import nacl.public


class Crypto:

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        return Crypto.secret_box(ak).encrypt(plain, nonce)

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        return Crypto.secret_box(ak).decrypt(ciphertext, nonce)

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        return Crypto.box(private_key, public_key).encrypt(ak, nonce)

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        return Crypto.box(private_key, public_key).decrypt(eak, nonce)

    @classmethod
    def box(self, private_key, public_key):
        return nacl.public.Box(private_key, public_key)

    @classmethod
    def secret_box(self, key):
        return nacl.secret.SecretBox(key)

    @classmethod
    def decode_public_key(self, key):
        return nacl.public.PublicKey(Crypto.base64decode(str(key)))

    @classmethod
    def encode_public_key(self, key):
        return Crypto.base64encode(key)

    @classmethod
    def decode_private_key(self, key):
        return nacl.public.PrivateKey(Crypto.base64decode(str(key)))

    @classmethod
    def encode_private_key(self, key):
        return Crypto.base64encode(key)

    @classmethod
    def random_key(self):
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    @classmethod
    def random_nonce(self):
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

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

    @classmethod
    def generate_keypair(self):
        # return public, private
        key = nacl.public.PrivateKey.generate()
        return key.public_key, key
