import sys
import json
import hashlib

try:
    import sha3
except ImportError:
    from warnings import warn
    warn("sha3 is not working!")

if sys.version_info.major == 3:
    def byte_to_hex(x):
        return x.hex()
else:
    import binascii
    byte_to_hex = binascii.hexlify


hex_to_byte = bytearray.fromhex


def get_hash_func(hash_type):
    supported_hash_types = {
        'sha256', 'md5', 'sha224', 'sha384', 'sha512',
        'sha3_256', 'sha3_224', 'sha3_384', 'sha3_512'
    }
    hash_type = hash_type.lower()
    if hash_type not in supported_hash_types:
        raise NotImplementedError(
            "`hash_type` {} is not supported. Supported types are "
            "{}".format(hash_type, supported_hash_types)
        )
    return getattr(hashlib, hash_type)


def compute_hash(data, hash_type="sha256"):
    hash_func = get_hash_func(hash_type)
    json_data = str.encode(json.dumps(data, sort_keys=True))
    sha = hash_func(json_data)
    return byte_to_hex(sha.digest())
