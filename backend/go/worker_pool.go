// Package main implements a bounded worker pool that processes jobs from a
// shared channel using a fixed number of goroutines. Shutdown is driven by
// context cancellation: in-flight jobs are allowed to finish, but no new
// jobs are dispatched once the context is done.
package main

import (
	"context"
	"fmt"
	"sync"
	"time"
)

// Job represents a unit of work to be executed by a worker.
type Job func(ctx context.Context) error

// Pool is a fixed-size pool of worker goroutines consuming Jobs.
type Pool struct {
	jobs chan Job
	wg   sync.WaitGroup
}

// NewPool creates a pool with n workers and starts them immediately.
// Workers exit when ctx is cancelled and the jobs channel is drained/closed.
func NewPool(ctx context.Context, n int) *Pool {
	p := &Pool{jobs: make(chan Job)}
	for i := 0; i < n; i++ {
		p.wg.Add(1)
		go p.worker(ctx, i)
	}
	return p
}

func (p *Pool) worker(ctx context.Context, id int) {
	defer p.wg.Done()
	for {
		select {
		case <-ctx.Done():
			return
		case job, ok := <-p.jobs:
			if !ok {
				return
			}
			if err := job(ctx); err != nil {
				fmt.Printf("worker %d: job error: %v\n", id, err)
			}
		}
	}
}

// Submit enqueues a job, respecting cancellation so callers don't block
// forever if the pool is shutting down.
func (p *Pool) Submit(ctx context.Context, j Job) error {
	select {
	case p.jobs <- j:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// Close stops accepting new jobs and waits for workers to finish.
func (p *Pool) Close() {
	close(p.jobs)
	p.wg.Wait()
}

func main() {
	ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
	defer cancel()

	pool := NewPool(ctx, 4)

	for i := 0; i < 10; i++ {
		id := i
		err := pool.Submit(ctx, func(ctx context.Context) error {
			time.Sleep(100 * time.Millisecond)
			fmt.Printf("processed job %d\n", id)
			return nil
		})
		if err != nil {
			fmt.Printf("submit job %d failed: %v\n", id, err)
			break
		}
	}

	pool.Close()
}
