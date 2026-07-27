/**
 * A generic singly linked list implementation supporting append, prepend,
 * delete, and reverse operations.
 */

class ListNode<T> {
  value: T;
  next: ListNode<T> | null = null;

  constructor(value: T) {
    this.value = value;
  }
}

class SinglyLinkedList<T> {
  private head: ListNode<T> | null = null;
  private tail: ListNode<T> | null = null;
  private size = 0;

  get length(): number {
    return this.size;
  }

  // Adds a new node with the given value to the end of the list.
  append(value: T): void {
    const node = new ListNode(value);
    if (!this.head || !this.tail) {
      this.head = node;
      this.tail = node;
    } else {
      this.tail.next = node;
      this.tail = node;
    }
    this.size++;
  }

  // Adds a new node with the given value to the start of the list.
  prepend(value: T): void {
    const node = new ListNode(value);
    node.next = this.head;
    this.head = node;
    if (!this.tail) {
      this.tail = node;
    }
    this.size++;
  }

  // Deletes the first node matching the given value. Returns true if removed.
  delete(value: T): boolean {
    if (!this.head) return false;

    if (this.head.value === value) {
      this.head = this.head.next;
      if (!this.head) this.tail = null;
      this.size--;
      return true;
    }

    let current = this.head;
    while (current.next) {
      if (current.next.value === value) {
        current.next = current.next.next;
        if (!current.next) this.tail = current; // deleted node was the tail
        this.size--;
        return true;
      }
      current = current.next;
    }
    return false;
  }

  // Reverses the list in place.
  reverse(): void {
    let prev: ListNode<T> | null = null;
    let current = this.head;
    this.tail = this.head;

    while (current) {
      const next: ListNode<T> | null = current.next;
      current.next = prev;
      prev = current;
      current = next;
    }
    this.head = prev;
  }

  // Returns the list's values as an array, in order from head to tail.
  toArray(): T[] {
    const result: T[] = [];
    let current = this.head;
    while (current) {
      result.push(current.value);
      current = current.next;
    }
    return result;
  }
}

export { SinglyLinkedList, ListNode };
