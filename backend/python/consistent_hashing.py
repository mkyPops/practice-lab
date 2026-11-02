"""
Consistent hashing ring.

Distributes keys across a set of nodes using consistent hashing with
virtual nodes (replicas) for better load balancing. Adding or removing
a node only remaps the keys that hashed near that node on the ring,
instead of reshuffling the entire keyspace.
"""

import bisect
import hashlib


class ConsistentHashRing:
    def __init__(self, nodes=None, replicas=100):
        self.replicas = replicas
        self._ring = {}          # hash value -> node name
        self._sorted_keys = []   # sorted list of hash values for bisect lookups
        for node in nodes or []:
            self.add_node(node)

    @staticmethod
    def _hash(key):
        # Use md5 for a well-distributed 128-bit hash, truncated to an int.
        digest = hashlib.md5(key.encode("utf-8")).digest()
        return int.from_bytes(digest, byteorder="big")

    def add_node(self, node):
        for i in range(self.replicas):
            vnode_key = f"{node}#{i}"
            h = self._hash(vnode_key)
            self._ring[h] = node
            bisect.insort(self._sorted_keys, h)

    def remove_node(self, node):
        for i in range(self.replicas):
            vnode_key = f"{node}#{i}"
            h = self._hash(vnode_key)
            del self._ring[h]
            pos = bisect.bisect_left(self._sorted_keys, h)
            if pos < len(self._sorted_keys) and self._sorted_keys[pos] == h:
                self._sorted_keys.pop(pos)

    def get_node(self, key):
        if not self._ring:
            raise KeyError("No nodes available in the ring")
        h = self._hash(key)
        pos = bisect.bisect(self._sorted_keys, h)
        # Wrap around to the first node if we're past the last hash value.
        if pos == len(self._sorted_keys):
            pos = 0
        return self._ring[self._sorted_keys[pos]]

    @property
    def nodes(self):
        return sorted(set(self._ring.values()))


if __name__ == "__main__":
    ring = ConsistentHashRing(nodes=["node-a", "node-b", "node-c"])

    sample_keys = [f"key-{i}" for i in range(10)]
    before = {k: ring.get_node(k) for k in sample_keys}
    print("Before adding node-d:", before)

    ring.add_node("node-d")
    after = {k: ring.get_node(k) for k in sample_keys}
    print("After adding node-d: ", after)

    moved = [k for k in sample_keys if before[k] != after[k]]
    print(f"Keys remapped: {len(moved)}/{len(sample_keys)} -> {moved}")
