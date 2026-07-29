// Package main implements a thread-safe token bucket rate limiter.
// Tokens are added to the bucket at a fixed rate up to a maximum capacity,
// and each request consumes one token. If no tokens are available, the
// request is rejected (non-blocking Allow) rather than waiting.
package main

import (
	"fmt"
	"sync"
	"time"
)

// TokenBucket implements the token bucket rate limiting algorithm.
type TokenBucket struct {
	mu         sync.Mutex
	capacity   float64
	tokens     float64
	refillRate float64 // tokens added per second
	lastRefill time.Time
}

// NewTokenBucket creates a bucket with the given capacity and refill rate
// (tokens per second). It starts full.
func NewTokenBucket(capacity, refillRate float64) *TokenBucket {
	return &TokenBucket{
		capacity:   capacity,
		tokens:     capacity,
		refillRate: refillRate,
		lastRefill: time.Now(),
	}
}

// Allow attempts to consume one token. It returns true if a token was
// available and consumed, false otherwise.
func (tb *TokenBucket) Allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	tb.refill()
	if tb.tokens >= 1 {
		tb.tokens--
		return true
	}
	return false
}

// refill adds tokens based on elapsed time since the last refill,
// capping at the bucket's capacity. Caller must hold the lock.
func (tb *TokenBucket) refill() {
	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tb.tokens += elapsed * tb.refillRate
	if tb.tokens > tb.capacity {
		tb.tokens = tb.capacity
	}
	tb.lastRefill = now
}

func main() {
	limiter := NewTokenBucket(5, 2) // capacity 5, refill 2 tokens/sec

	var wg sync.WaitGroup
	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			if limiter.Allow() {
				fmt.Printf("request %d: allowed\n", id)
			} else {
				fmt.Printf("request %d: rejected\n", id)
			}
		}(i)
	}
	wg.Wait()
}
