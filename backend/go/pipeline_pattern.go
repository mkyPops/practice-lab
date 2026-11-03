// Package main demonstrates a multi-stage data processing pipeline using
// Go channels. Each stage runs in its own goroutine, transforming data and
// passing it downstream until a final stage aggregates the results.
package main

import (
	"fmt"
)

// generate emits integers 1..n onto a channel, then closes it.
func generate(n int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for i := 1; i <= n; i++ {
			out <- i
		}
	}()
	return out
}

// square reads integers from in, squares them, and sends the results on.
func square(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for v := range in {
			out <- v * v
		}
	}()
	return out
}

// filterEven passes through only even values.
func filterEven(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for v := range in {
			if v%2 == 0 {
				out <- v
			}
		}
	}()
	return out
}

// sum consumes all values from in and returns their total.
func sum(in <-chan int) int {
	total := 0
	for v := range in {
		total += v
	}
	return total
}

func main() {
	// Wire up the pipeline: generate -> square -> filterEven -> sum.
	numbers := generate(10)
	squared := square(numbers)
	evens := filterEven(squared)
	result := sum(evens)

	fmt.Printf("Sum of even squares from 1..10: %d\n", result)
}
