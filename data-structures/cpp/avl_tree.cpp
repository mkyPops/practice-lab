// AVL self-balancing binary search tree.
// Supports insertion (with automatic rotations to maintain balance) and search.

#include <iostream>
#include <algorithm>
#include <memory>

struct Node {
    int key;
    int height;
    std::unique_ptr<Node> left, right;
    explicit Node(int k) : key(k), height(1) {}
};

class AVLTree {
public:
    void insert(int key) { root_ = insert(std::move(root_), key); }

    bool search(int key) const {
        Node* cur = root_.get();
        while (cur) {
            if (key == cur->key) return true;
            cur = key < cur->key ? cur->left.get() : cur->right.get();
        }
        return false;
    }

private:
    std::unique_ptr<Node> root_;

    static int height(const Node* n) { return n ? n->height : 0; }

    static int balanceFactor(const Node* n) {
        return n ? height(n->left.get()) - height(n->right.get()) : 0;
    }

    static void updateHeight(Node* n) {
        n->height = 1 + std::max(height(n->left.get()), height(n->right.get()));
    }

    // Right rotation: pivot's left child becomes new root of subtree.
    static std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> pivot) {
        std::unique_ptr<Node> newRoot = std::move(pivot->left);
        pivot->left = std::move(newRoot->right);
        updateHeight(pivot.get());
        newRoot->right = std::move(pivot);
        updateHeight(newRoot.get());
        return newRoot;
    }

    // Left rotation: pivot's right child becomes new root of subtree.
    static std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> pivot) {
        std::unique_ptr<Node> newRoot = std::move(pivot->right);
        pivot->right = std::move(newRoot->left);
        updateHeight(pivot.get());
        newRoot->left = std::move(pivot);
        updateHeight(newRoot.get());
        return newRoot;
    }

    static std::unique_ptr<Node> insert(std::unique_ptr<Node> node, int key) {
        if (!node) return std::make_unique<Node>(key);

        if (key < node->key) {
            node->left = insert(std::move(node->left), key);
        } else if (key > node->key) {
            node->right = insert(std::move(node->right), key);
        } else {
            return node; // duplicate keys not inserted
        }

        updateHeight(node.get());
        int balance = balanceFactor(node.get());

        // Left-heavy cases
        if (balance > 1) {
            if (balanceFactor(node->left.get()) < 0)
                node->left = rotateLeft(std::move(node->left)); // Left-Right case
            return rotateRight(std::move(node));
        }
        // Right-heavy cases
        if (balance < -1) {
            if (balanceFactor(node->right.get()) > 0)
                node->right = rotateRight(std::move(node->right)); // Right-Left case
            return rotateLeft(std::move(node));
        }

        return node;
    }
};

int main() {
    AVLTree tree;
    int values[] = {10, 20, 30, 40, 50, 25};
    for (int v : values) tree.insert(v);

    for (int v : {25, 5, 40}) {
        std::cout << "Search " << v << ": "
                  << (tree.search(v) ? "found" : "not found") << "\n";
    }
    return 0;
}
