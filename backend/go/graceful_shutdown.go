// Package main implements an HTTP server that listens for OS interrupt/
// termination signals and performs a graceful shutdown, draining in-flight
// requests within a configurable timeout before exiting.
package main

import (
	"context"
	"errors"
	"flag"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
)

func main() {
	addr := flag.String("addr", ":8080", "address to listen on")
	drainTimeout := flag.Duration("drain-timeout", 15*time.Second, "max time to wait for in-flight requests to finish")
	flag.Parse()

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	srv := &http.Server{
		Addr:    *addr,
		Handler: mux,
	}

	// Run the server in a goroutine so we can listen for shutdown signals
	// on the main goroutine.
	go func() {
		log.Printf("listening on %s", *addr)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("server error: %v", err)
		}
	}()

	// Block until an interrupt or termination signal is received.
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
	sig := <-sigCh
	log.Printf("received signal %s, initiating graceful shutdown", sig)

	// Give active connections up to drainTimeout to finish before forcing
	// shutdown.
	ctx, cancel := context.WithTimeout(context.Background(), *drainTimeout)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("graceful shutdown failed: %v; forcing close", err)
		if cerr := srv.Close(); cerr != nil {
			log.Fatalf("forced close failed: %v", cerr)
		}
		return
	}

	log.Println("server shut down cleanly")
}
