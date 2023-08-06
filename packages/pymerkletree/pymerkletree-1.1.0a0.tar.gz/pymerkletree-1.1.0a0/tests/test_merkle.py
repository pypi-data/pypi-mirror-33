import hashlib
from pytest import raises, mark

from pymerkletree import MerkleTree, hex_to_byte, is_proof_valid


_value_hash_pair = [
    ("a", 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'),
    ("b", '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d'),
    ("c", '2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6'),
    ("d", '18ac3e7343f016890c510e93f935261169d9e3f565436429830faf0934f4f8e4'),
    ("e", '3f79bb7b435b05321651daefd374cdc681dc06faa65e374e38337b88ca046dea'),
]


def _load_merkle_trees():
    values, hashes = zip(*_value_hash_pair)
    mt1 = MerkleTree()
    mt1.add_leaves(values, True)
    mt2 = MerkleTree()
    mt2.add_leaves(hashes, False)
    mt3 = MerkleTree()
    for v in values:
        mt3.add_leaves(v, True)
    return [mt1, mt2, mt3]


@mark.parametrize("mt", _load_merkle_trees())
def test_add_leaves(mt):
    expected_root = ("d71f8983ad4ee170f8129f1ebcdd7440be7798d8e1c80420"
                     "bf11f1eced610dba")
    assert 5 == mt.num_leaves
    assert expected_root == mt.merkle_root


def test_init_raises():
    raises(NotImplementedError, MerkleTree, "sha_dummy")


def test_merkle_root_raises():
    mt = MerkleTree()
    with raises(ValueError):
        _ = mt.merkle_root


def test_merkle_root_basics():
    v_left, v_right = (
        'a292780cc748697cb499fdcc8cb89d835609f11e502281dfe3f6690b1cc23dcb',
        'cb4990b9a8936bbc137ddeb6dcab4620897b099a450ecdc5f3e86ef4b3a7135c'
    )
    expected_root = hashlib.sha256(
        hex_to_byte(v_left) + hex_to_byte(v_right)
    ).hexdigest()

    mt = MerkleTree()
    mt.add_leaves([v_left, v_right], False)
    assert expected_root == mt.merkle_root
    mt.add_leaves(v_right, False)
    assert expected_root != mt.merkle_root


def test_merkle_root_one_leaf():
    mt = MerkleTree()
    v_hex = 'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'
    mt.add_leaves(v_hex, False)
    assert mt.is_tree_ready
    assert v_hex == mt.get_leaf(0)
    assert v_hex == mt.merkle_root


def test_get_proof_two_leaves():
    v_left, v_right = (
        'a292780cc748697cb499fdcc8cb89d835609f11e502281dfe3f6690b1cc23dcb',
        'cb4990b9a8936bbc137ddeb6dcab4620897b099a450ecdc5f3e86ef4b3a7135c'
    )
    mt = MerkleTree()
    mt.add_leaves([v_left, v_right], False)
    assert [{"right": v_right}] == mt.get_proof(0)
    assert [{"left": v_left}] == mt.get_proof(1)


def test_get_proof_three_leaves():
    mt = MerkleTree()
    mt.add_leaves(list("abc"), do_hash=True)
    proof = mt.get_proof(1)
    expected = [
        {"left": _value_hash_pair[0][1]},
        {"right":
         "2e7d2c03a9507ae265ecf5b5356885a53393a2029d241394997265a1a25aefc6"}
    ]
    assert expected == proof
    assert is_proof_valid(proof, mt.get_leaf(1), mt.merkle_root)


def test_is_proof_valid_five_leaves():
    mt = MerkleTree()
    values, _ = zip(*_value_hash_pair)
    mt.add_leaves(values, True)
    proof_3 = mt.get_proof(3)
    assert is_proof_valid(proof_3, _value_hash_pair[3][1], mt.merkle_root)
    assert not is_proof_valid(proof_3, _value_hash_pair[2][1], mt.merkle_root)
    expected_proof_4 = [
        {"left":
         "14ede5e8e97ad9372327728f5099b95604a39593cac3bd38a343ad76205213e7"}
    ]
    assert expected_proof_4 == mt.get_proof(4)


@mark.parametrize("hash_type,expected_root", [
    ("sha224", "8004070edc6bb1c173c662305ba7938b8ba576f0bf74daecab1d7760"),
    ("sha3_224", "c339999aa697ec4814f141c1e67ce782764b1264056e7d48bd14b40a"),

    ("sha256",
     "e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a"),
    ("sha3_256",
     "29df505440ebe180c00857e92b0694c56a33762b08944472492b0cbf6ec607e3"),

    ("sha384",
     "03f4842cf39605e9f5eb3fdddffa6c3a4d70dcb60b39a9270747c3745a4a9198"
     "a7c96ab0fd4b7e628623f68a0a73452b"),
    ("sha3_384",
     "ae23be22060aacaac7d0d94c91376cdd969e7fde06885c969c4a41d17e2f2980"
     "1efef3476c123abba6b73b01f3bd0817"),

    ("sha512",
     "a40fb6247bf9aa223348eb8c99dcea9d198694b805ae85bcbfd5ffd33f8ef42c"
     "07dd4946ffa68654fd19026ee2723d7ecb2868c3134ce960981156b2120ef62c"),
    ("sha3_512",
     "ae374b1dd25ad291e944b5802e376a5ed8ef671e14e086dc72933246a708b92c"
     "65dd3b46c17de1f752136b11ef7e48c42acbeae77c6dcbf3fe605963785a235e"),

    ("md5", "96e024ba2074fe77e8e965ba43a704be"),
])
def test_is_proof_valid_other_hash_types(hash_type, expected_root):
    mt = MerkleTree(hash_type=hash_type)
    values, _ = zip(*_value_hash_pair)
    mt.add_leaves(values[:2], True)
    assert expected_root == mt.merkle_root
    proof = mt.get_proof(1)
    assert [{"left": mt.get_leaf(0)}] == proof
    assert is_proof_valid(proof, mt.get_leaf(1), mt.merkle_root, hash_type)
    assert not is_proof_valid(proof, mt.get_leaf(0), mt.merkle_root, hash_type)
