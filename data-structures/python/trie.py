"""
A simple Trie (prefix tree) implementation supporting insertion,
exact word search, and prefix lookup.
"""


class TrieNode:
    """A single node in the Trie, holding children and a word-end flag."""

    __slots__ = ("children", "is_end")

    def __init__(self):
        self.children = {}
        self.is_end = False


class Trie:
    """A prefix tree supporting insert, search, and startsWith operations."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        """Insert a word into the trie."""
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end = True

    def search(self, word: str) -> bool:
        """Return True if the exact word exists in the trie."""
        node = self._find_node(word)
        return node is not None and node.is_end

    def startsWith(self, prefix: str) -> bool:
        """Return True if any word in the trie starts with the given prefix."""
        return self._find_node(prefix) is not None

    def _find_node(self, prefix: str):
        """Walk the trie following prefix; return the final node or None."""
        node = self.root
        for char in prefix:
            node = node.children.get(char)
            if node is None:
                return None
        return node


if __name__ == "__main__":
    trie = Trie()
    trie.insert("apple")

    print(trie.search("apple"))    # True
    print(trie.search("app"))      # False
    print(trie.startsWith("app"))  # True

    trie.insert("app")
    print(trie.search("app"))      # True
