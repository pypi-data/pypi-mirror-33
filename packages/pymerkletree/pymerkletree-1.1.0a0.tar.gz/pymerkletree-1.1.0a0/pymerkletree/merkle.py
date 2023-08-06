from .utils import get_hash_func, hex_to_byte, byte_to_hex


class MerkleTree(object):

    _is_left_node_sibling_map = {
        True: ("right", 1), False: ("left", -1)
    }

    def __init__(self, hash_type="sha256"):
        self.hash_func = get_hash_func(hash_type)
        self.levels = [[]]

    @property
    def leaves(self):
        return self.levels[-1]

    @property
    def num_leaves(self):
        return len(self.leaves)

    @property
    def is_tree_ready(self):
        return len(self.levels) > 1 or self.num_leaves == 1

    def add_leaves(self, values, do_hash=True):
        if not isinstance(values, (list, tuple)):
            values = [values]
        if do_hash:
            values = map(
                lambda v: self.hash_func(str.encode(v)).hexdigest(), values
            )
        values = map(hex_to_byte, values)
        self.leaves.extend(values)
        if self.is_tree_ready:
            self.levels = [self.leaves]

    def get_leaf(self, index):
        return byte_to_hex(self.leaves[index])

    def _make_tree(self):
        if self.is_tree_ready:
            return
        if self.num_leaves == 0:
            raise ValueError("No leaf to make tree!")
        while len(self.levels[0]) > 1:
            self._calculate_next_level()

    def _calculate_next_level(self):
        current_level = self.levels[0]
        num_leaves_current_level = len(current_level)
        new_level = [
            self.hash_func(current_level[i] + current_level[i+1]).digest()
            for i in range(0, num_leaves_current_level - 1, 2)
        ]
        if num_leaves_current_level % 2 == 1:
            new_level.append(current_level[-1])
        self.levels = [new_level] + self.levels

    @property
    def merkle_root(self):
        self._make_tree()
        return byte_to_hex(self.levels[0][0])

    def get_proof(self, index):
        self._make_tree()
        proof = []
        for current_level in self.levels[::-1]:
            is_left_node = index % 2 == 0
            is_solo_node = (index == len(current_level) - 1 and is_left_node)
            if not is_solo_node:
                sibling_pos, offset = \
                    self._is_left_node_sibling_map[is_left_node]
                sibling_value = byte_to_hex(
                    current_level[index + offset]
                )
                proof.append({sibling_pos: sibling_value})
            index = int(index / 2.)
        return proof


def is_proof_valid(proof, target_hash, merkle_root, hash_type="sha256"):
    proof_hash_byte = hex_to_byte(target_hash)
    hash_func = get_hash_func(hash_type)
    for leaf in proof:
        sibling_pos, sibling_hash = list(leaf.items())[0]
        sibling_hash_byte = hex_to_byte(sibling_hash)
        if sibling_pos == "left":
            info = sibling_hash_byte + proof_hash_byte
        else:
            info = proof_hash_byte + sibling_hash_byte
        proof_hash_byte = hash_func(info).digest()
    return byte_to_hex(proof_hash_byte) == merkle_root
