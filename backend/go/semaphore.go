// Package main implements a simple counting semaphore built on top of a
// buffered channel. It can be used to limit the number of goroutines that
// may execute a given section of code concurrently.
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Semaphore limits concurrent access to a resource to at most N holders.
type Semaphore struct {
	tokens chan struct{}
}

// NewSemaphore creates a semaphore that allows up to n concurrent acquisitions.
func NewSemaphore(n int) *Semaphore {
	if n <= 0 {
		panic("semaphore: n must be greater than zero")
	}
	return &Semaphore{tokens: make(chan struct{}, n)}
}

// Acquire blocks until a slot is available or ctx is canceled.
func (s *Semaphore) Acquire(ctx context.Context) error {
	select {
	case s.tokens <- struct{}{}:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// TryAcquire attempts to acquire a slot without blocking.
// It returns true if the slot was acquired.
func (s *Semaphore) TryAcquire() bool {
	select {
	case s.tokens <- struct{}{}:
		return true
	default:
		return false
	}
}

// Release frees up a previously acquired slot.
func (s *Semaphore) Release() {
	select {
	case <-s.tokens:
	default:
		// Release called without a matching Acquire; ignore to avoid panic.
	}
}

func main() {
	sem := NewSemaphore(3) // allow at most 3 concurrent workers
	var wg sync.WaitGroup

	for i := 1; i <= 10; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()

			ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
			defer cancel()

			if err := sem.Acquire(ctx); err != nil {
				fmt.Printf("worker %d: failed to acquire: %v\n", id, err)
				return
			}
			defer sem.Release()

			fmt.Printf("worker %d: running\n", id)
			time.Sleep(300 * time.Millisecond)
			fmt.Printf("worker %d: done\n", id)
		}(i)
	}

	wg.Wait()
}
