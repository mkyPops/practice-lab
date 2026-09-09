// Package main demonstrates a simple semaphore primitive built on top of a
// buffered channel, used to limit the number of goroutines that may execute
// a critical section concurrently.
package main

import (
	"fmt"
	"sync"
	"time"
)

// Semaphore restricts concurrent access to a resource to a fixed number of
// holders. It is implemented using a buffered channel as the counting
// mechanism: acquiring blocks when the channel is full, and releasing frees
// a slot for the next waiter.
type Semaphore struct {
	slots chan struct{}
}

// NewSemaphore creates a Semaphore that allows up to n concurrent holders.
func NewSemaphore(n int) *Semaphore {
	if n <= 0 {
		panic("semaphore: n must be positive")
	}
	return &Semaphore{slots: make(chan struct{}, n)}
}

// Acquire blocks until a slot is available, then claims it.
func (s *Semaphore) Acquire() {
	s.slots <- struct{}{} // blocks if channel buffer is full
}

// Release frees a previously acquired slot.
func (s *Semaphore) Release() {
	<-s.slots
}

// TryAcquire attempts to claim a slot without blocking, reporting success.
func (s *Semaphore) TryAcquire() bool {
	select {
	case s.slots <- struct{}{}:
		return true
	default:
		return false
	}
}

func main() {
	const maxConcurrent = 3
	sem := NewSemaphore(maxConcurrent)

	var wg sync.WaitGroup
	for i := 1; i <= 10; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()

			sem.Acquire()
			defer sem.Release()

			fmt.Printf("worker %d: started\n", id)
			time.Sleep(200 * time.Millisecond) // simulate work
			fmt.Printf("worker %d: finished\n", id)
		}(i)
	}

	wg.Wait()
	fmt.Println("all workers completed")
}
