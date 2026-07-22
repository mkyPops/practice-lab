/**
 * A generic Binary Search Tree (BST) implementation.
 * Supports insertion, search, and in-order traversal (returns sorted keys).
 * Duplicate keys are ignored on insert.
 */

class BSTNode<T> {
  value: T;
  left: BSTNode<T> | null = null;
  right: BSTNode<T> | null = null;

  constructor(value: T) {
    this.value = value;
  }
}

export class BinarySearchTree<T> {
  private root: BSTNode<T> | null = null;

  // Comparator defaults to standard relational operators, but can be
  // overridden for custom ordering (e.g. objects with a sort key).
  constructor(private readonly compare: (a: T, b: T) => number = (a, b) =>
    a < b ? -1 : a > b ? 1 : 0
  ) {}

  /** Inserts a value into the tree, ignoring duplicates. */
  insert(value: T): void {
    this.root = this.insertNode(this.root, value);
  }

  private insertNode(node: BSTNode<T> | null, value: T): BSTNode<T> {
    if (node === null) {
      return new BSTNode(value);
    }
    const cmp = this.compare(value, node.value);
    if (cmp < 0) {
      node.left = this.insertNode(node.left, value);
    } else if (cmp > 0) {
      node.right = this.insertNode(node.right, value);
    }
    // cmp === 0 means duplicate; do nothing.
    return node;
  }

  /** Returns true if the value exists in the tree. */
  search(value: T): boolean {
    let node = this.root;
    while (node !== null) {
      const cmp = this.compare(value, node.value);
      if (cmp === 0) return true;
      node = cmp < 0 ? node.left : node.right;
    }
    return false;
  }

  /** Returns all values in sorted (ascending) order. */
  inOrderTraversal(): T[] {
    const result: T[] = [];
    this.inOrder(this.root, result);
    return result;
  }

  private inOrder(node: BSTNode<T> | null, result: T[]): void {
    if (node === null) return;
    this.inOrder(node.left, result);
    result.push(node.value);
    this.inOrder(node.right, result);
  }
}

// Example usage:
// const bst = new BinarySearchTree<number>();
// [5, 3, 8, 1, 4, 7, 9].forEach((n) => bst.insert(n));
// console.log(bst.inOrderTraversal()); // [1, 3, 4, 5, 7, 8, 9]
// console.log(bst.search(7)); // true
// console.log(bst.search(6)); // false
