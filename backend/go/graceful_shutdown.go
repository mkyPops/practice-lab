// Package main implements an HTTP server that listens for OS interrupt/termination
// signals and performs a graceful shutdown, allowing in-flight requests to
// complete within a configurable drain timeout before the process exits.
package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

const (
	addr           = ":8080"
	drainTimeout   = 15 * time.Second
	readTimeout    = 5 * time.Second
	writeTimeout   = 10 * time.Second
	idleTimeout    = 60 * time.Second
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		// Simulate some work so shutdown behavior is observable.
		time.Sleep(2 * time.Second)
		w.Write([]byte("hello\n"))
	})

	srv := &http.Server{
		Addr:         addr,
		Handler:      mux,
		ReadTimeout:  readTimeout,
		WriteTimeout: writeTimeout,
		IdleTimeout:  idleTimeout,
	}

	// Run the server in a goroutine so the main goroutine can wait for signals.
	go func() {
		log.Printf("listening on %s", addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("listen error: %v", err)
		}
	}()

	// Wait for SIGINT or SIGTERM.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	sig := <-stop
	log.Printf("received signal %s, starting graceful shutdown", sig)

	// Bound the shutdown by the configured drain timeout.
	ctx, cancel := context.WithTimeout(context.Background(), drainTimeout)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("graceful shutdown failed: %v, forcing close", err)
		if cerr := srv.Close(); cerr != nil {
			log.Fatalf("force close failed: %v", cerr)
		}
	}

	log.Println("server stopped")
}
