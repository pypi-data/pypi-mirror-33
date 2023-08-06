from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import sha3
from cryptoconditions import crypto
import nacl.signing
from collections import namedtuple

_DB_INSTANCE = None


def get_database_instance(config_file=None):
    global _DB_INSTANCE
    if _DB_INSTANCE is None:
        _DB_INSTANCE = BigchainDBInstance(config_file)

    return _DB_INSTANCE


class BigchainDBInstance(object):

    def __init__(self, config):
        host = config['db.hostname']
        port = int(config['db.port'])
        app_id = config['db.app_id']
        app_key = config['db.app_key']
        bdb_root_url = '%s:%s' % (host, port)
        # bdb_root_url = 'https://%s:%s' % (host, port)
        tokens = {'app_id': app_id, 'app_key': app_key}

        self._bdb = BigchainDB(bdb_root_url, headers=tokens)

    @property
    def instance(self):
        return self._bdb


CryptoKeypair = namedtuple('CryptoKeypair', ('private_key', 'public_key'))


class Ed25519SigningKeyFromHash(crypto.Ed25519SigningKey):

    def __init__(self, key, encoding='base58'):
        super().__init__(key, encoding=encoding)

    @classmethod
    def generate(cls, hash_bytes):
        return cls(nacl.signing.SigningKey(hash_bytes).encode(encoder=crypto.Base58Encoder))


def ed25519_generate_key_pair_from_secret(secret):
    """
    Generate a new key pair.
    Args:
        secret (:class:`string`): A secret that serves as a seed
    Returns:
        A tuple of (private_key, public_key) encoded in base58.
    """

    # if you want to do this correctly, use a key derivation function!
    if not isinstance(secret, bytes):
        secret = secret.encode()

    hash_bytes = sha3.keccak_256(secret).digest()
    sk = Ed25519SigningKeyFromHash.generate(hash_bytes=hash_bytes)
    # Private key
    private_value_base58 = sk.encode(encoding='base58')

    # Public key
    public_value_compressed_base58 = sk.get_verifying_key().encode(encoding='base58')

    return private_value_base58, public_value_compressed_base58


def generate_key_pair(secret=None):
    """Generates a cryptographic key pair.
    Args:
        secret (:class:`string`): A secret that serves as a seed
    Returns:
        :class:`~bigchaindb.common.crypto.CryptoKeypair`: A
        :obj:`collections.namedtuple` with named fields
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.private_key` and
        :attr:`~bigchaindb.common.crypto.CryptoKeypair.public_key`.
    """
    if secret:
        keypair_raw = ed25519_generate_key_pair_from_secret(secret)
        return CryptoKeypair(
            *(k.decode() for k in keypair_raw))
    else:
        return generate_keypair()
