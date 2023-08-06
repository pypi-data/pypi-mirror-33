from base_crypto import BaseCrypto
import nacl.utils
import nacl.secret
import nacl.public


class SodiumCrypto(BaseCrypto):

    @classmethod
    def get_mode(self):
        return 'sodium'

    @classmethod
    def encrypt_secret(self, ak, plain, nonce):
        return self.secret_box(ak).encrypt(plain, nonce)

    @classmethod
    def decrypt_secret(self, ak, ciphertext, nonce):
        return self.secret_box(ak).decrypt(ciphertext, nonce)

    @classmethod
    def encrypt_ak(self, private_key, public_key, ak, nonce):
        return self.box(private_key, public_key).encrypt(ak, nonce)

    @classmethod
    def decrypt_eak(self, private_key, public_key, eak, nonce):
        return self.box(private_key, public_key).decrypt(eak, nonce)

    @classmethod
    def box(self, private_key, public_key):
        return nacl.public.Box(private_key, public_key)

    @classmethod
    def secret_box(self, key):
        return nacl.secret.SecretBox(key)

    @classmethod
    def decode_public_key(self, key):
        return nacl.public.PublicKey(BaseCrypto.base64decode(str(key)))

    @classmethod
    def encode_public_key(self, key):
        return BaseCrypto.base64encode(key)

    @classmethod
    def decode_private_key(self, key):
        return nacl.public.PrivateKey(BaseCrypto.base64decode(str(key)))

    @classmethod
    def encode_private_key(self, key):
        return BaseCrypto.base64encode(key)

    @classmethod
    def random_key(self):
        return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    @classmethod
    def random_nonce(self):
        return nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    @classmethod
    def generate_keypair(self):
        # return public, private
        key = nacl.public.PrivateKey.generate()
        return key.public_key, key
