"""
Segment tree supporting range sum queries and point updates in O(log n).

The tree is stored in a flat array of size 2*n (iterative implementation),
where leaves occupy indices [n, 2n) and each internal node i holds the sum
of its two children at 2*i and 2*i+1.
"""


class SegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (2 * self.n)
        # place initial values at the leaves
        self.tree[self.n:] = list(data)
        # build internal nodes bottom-up
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index, value):
        """Set data[index] = value and update affected sums."""
        pos = index + self.n
        self.tree[pos] = value
        # propagate change upward to the root
        pos //= 2
        while pos >= 1:
            self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]
            pos //= 2

    def query(self, left, right):
        """Return sum of data[left:right] (half-open interval)."""
        result = 0
        left += self.n
        right += self.n
        while left < right:
            if left & 1:
                result += self.tree[left]
                left += 1
            if right & 1:
                right -= 1
                result += self.tree[right]
            left //= 2
            right //= 2
        return result


if __name__ == "__main__":
    data = [1, 3, 5, 7, 9, 11]
    st = SegmentTree(data)

    print(st.query(1, 4))   # sum of data[1:4] -> 3+5+7 = 15
    st.update(2, 10)         # data becomes [1, 3, 10, 7, 9, 11]
    print(st.query(1, 4))   # 3+10+7 = 20
    print(st.query(0, 6))   # total sum = 41
