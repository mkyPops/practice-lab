// Package main demonstrates a multi-stage data processing pipeline built
// with Go channels. Numbers flow through generator -> square -> filter
// stages, and the final results are collected and printed by the consumer.
package main

import "fmt"

// generate emits integers 1..n on the returned channel.
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

// square reads integers from in, squares them, and sends results downstream.
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

// filterEven passes through only even values from in.
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

func main() {
	// Wire the pipeline stages together.
	numbers := generate(10)
	squared := square(numbers)
	evens := filterEven(squared)

	// Consume the final stage and accumulate the sum.
	sum := 0
	for v := range evens {
		fmt.Println("received:", v)
		sum += v
	}
	fmt.Println("sum of even squares:", sum)
}
