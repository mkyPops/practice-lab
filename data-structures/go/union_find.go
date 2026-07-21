// Package main implements a Disjoint Set Union (Union-Find) data structure
// with path compression and union by rank for near-constant-time operations.
package main

import "fmt"

// DSU represents a disjoint set union structure.
type DSU struct {
	parent []int
	rank   []int
}

// NewDSU creates a new DSU with n elements, each in its own set.
func NewDSU(n int) *DSU {
	d := &DSU{
		parent: make([]int, n),
		rank:   make([]int, n),
	}
	for i := range d.parent {
		d.parent[i] = i
	}
	return d
}

// Find returns the representative of the set containing x,
// applying path compression along the way.
func (d *DSU) Find(x int) int {
	if d.parent[x] != x {
		d.parent[x] = d.Find(d.parent[x]) // path compression
	}
	return d.parent[x]
}

// Union merges the sets containing x and y using union by rank.
// It returns true if a merge occurred, or false if they were already in the same set.
func (d *DSU) Union(x, y int) bool {
	rootX, rootY := d.Find(x), d.Find(y)
	if rootX == rootY {
		return false
	}

	// Attach the smaller-rank tree under the larger-rank tree's root.
	switch {
	case d.rank[rootX] < d.rank[rootY]:
		d.parent[rootX] = rootY
	case d.rank[rootX] > d.rank[rootY]:
		d.parent[rootY] = rootX
	default:
		d.parent[rootY] = rootX
		d.rank[rootX]++
	}
	return true
}

// Connected reports whether x and y belong to the same set.
func (d *DSU) Connected(x, y int) bool {
	return d.Find(x) == d.Find(y)
}

func main() {
	dsu := NewDSU(10)

	dsu.Union(1, 2)
	dsu.Union(2, 3)
	dsu.Union(4, 5)

	fmt.Println("1 and 3 connected:", dsu.Connected(1, 3)) // true
	fmt.Println("1 and 4 connected:", dsu.Connected(1, 4)) // false

	dsu.Union(3, 4)
	fmt.Println("1 and 5 connected after union(3,4):", dsu.Connected(1, 5)) // true
}
