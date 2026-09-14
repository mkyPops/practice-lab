"""
Consistent hashing ring implementation using virtual nodes to distribute keys
across a set of physical nodes. Adding or removing a node only remaps the
keys owned by that node's virtual nodes, minimizing overall reshuffling.
"""

import bisect
import hashlib


class ConsistentHashRing:
    def __init__(self, nodes=None, vnodes=100):
        # vnodes: number of virtual nodes per physical node, improves balance
        self.vnodes = vnodes
        self._ring = {}          # hash -> physical node name
        self._sorted_hashes = [] # sorted list of hashes for binary search
        for node in nodes or []:
            self.add_node(node)

    @staticmethod
    def _hash(key):
        digest = hashlib.md5(key.encode("utf-8")).digest()
        return int.from_bytes(digest, byteorder="big")

    def add_node(self, node):
        for i in range(self.vnodes):
            vnode_hash = self._hash(f"{node}#{i}")
            self._ring[vnode_hash] = node
            bisect.insort(self._sorted_hashes, vnode_hash)

    def remove_node(self, node):
        for i in range(self.vnodes):
            vnode_hash = self._hash(f"{node}#{i}")
            del self._ring[vnode_hash]
            idx = bisect.bisect_left(self._sorted_hashes, vnode_hash)
            self._sorted_hashes.pop(idx)

    def get_node(self, key):
        if not self._ring:
            raise ValueError("No nodes available in the ring")
        h = self._hash(key)
        idx = bisect.bisect(self._sorted_hashes, h)
        # wrap around the ring if past the last hash
        if idx == len(self._sorted_hashes):
            idx = 0
        return self._ring[self._sorted_hashes[idx]]


if __name__ == "__main__":
    ring = ConsistentHashRing(["node1", "node2", "node3"])
    keys = [f"key{i}" for i in range(10)]
    for k in keys:
        print(k, "->", ring.get_node(k))

    print("\nAdding node4...\n")
    ring.add_node("node4")
    for k in keys:
        print(k, "->", ring.get_node(k))
