// AVL self-balancing binary search tree supporting insert and search,
// with automatic left/right/left-right/right-left rotations after insertion.
#include <iostream>
#include <algorithm>
#include <memory>

struct Node {
    int key;
    int height;
    std::unique_ptr<Node> left;
    std::unique_ptr<Node> right;
    explicit Node(int k) : key(k), height(1) {}
};

class AVLTree {
public:
    void insert(int key) { root_ = insert(std::move(root_), key); }

    bool search(int key) const {
        const Node* cur = root_.get();
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

    // Standard right rotation: pulls left child up to become new subtree root.
    static std::unique_ptr<Node> rotateRight(std::unique_ptr<Node> y) {
        std::unique_ptr<Node> x = std::move(y->left);
        y->left = std::move(x->right);
        updateHeight(y.get());
        x->right = std::move(y);
        updateHeight(x.get());
        return x;
    }

    // Standard left rotation: pulls right child up to become new subtree root.
    static std::unique_ptr<Node> rotateLeft(std::unique_ptr<Node> x) {
        std::unique_ptr<Node> y = std::move(x->right);
        x->right = std::move(y->left);
        updateHeight(x.get());
        y->left = std::move(x);
        updateHeight(y.get());
        return y;
    }

    static std::unique_ptr<Node> insert(std::unique_ptr<Node> node, int key) {
        if (!node) return std::make_unique<Node>(key);

        if (key < node->key) {
            node->left = insert(std::move(node->left), key);
        } else if (key > node->key) {
            node->right = insert(std::move(node->right), key);
        } else {
            return node; // duplicate keys are ignored
        }

        updateHeight(node.get());
        int balance = balanceFactor(node.get());

        // Left-heavy cases
        if (balance > 1 && key < node->left->key)
            return rotateRight(std::move(node));
        if (balance > 1 && key > node->left->key) {
            node->left = rotateLeft(std::move(node->left));
            return rotateRight(std::move(node));
        }

        // Right-heavy cases
        if (balance < -1 && key > node->right->key)
            return rotateLeft(std::move(node));
        if (balance < -1 && key < node->right->key) {
            node->right = rotateRight(std::move(node->right));
            return rotateLeft(std::move(node));
        }

        return node;
    }
};

int main() {
    AVLTree tree;
    int values[] = {10, 20, 30, 40, 50, 25};
    for (int v : values) tree.insert(v);

    for (int v : {25, 100, 10, 999}) {
        std::cout << "search(" << v << ") = "
                  << (tree.search(v) ? "found" : "not found") << '\n';
    }
    return 0;
}
