from pytest import mark
from pymerkletree import utils


@mark.parametrize("hash_type,expected", [
    ("sha256",
     "cf494b434cb87365614c01c27506ea800119e556151965129fc3b98b11d4f10c"),
    ("sha224", "36b63daaa37b14164f8e08a6284e964359be4f4260162077666a1aa2"),
])
def test_compute_hash(hash_type, expected):
    data = ["2016-05-28", {"SHY": ".5", "SPY": ".5"}]
    assert expected == utils.compute_hash(data, hash_type=hash_type)


def test_byte_hex():
    v_hex = utils.compute_hash("0000")
    v_byte = utils.hex_to_byte(v_hex)
    assert v_hex == utils.byte_to_hex(v_byte)
