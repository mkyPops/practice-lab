// Package main implements a minimal HTTP server exposing /healthz and
// /readyz endpoints for use as container liveness and readiness probes.
//
// /healthz always returns 200 OK as long as the process is running and able
// to serve requests, indicating liveness.
//
// /readyz returns 200 OK only once the application has finished its startup
// work and is ready to accept traffic; it returns 503 otherwise. This lets
// orchestrators (e.g. Kubernetes) delay routing traffic until the app is
// truly ready, and restart the container if it becomes unresponsive.
package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"sync/atomic"
	"syscall"
	"time"
)

func main() {
	var ready atomic.Bool // flips to true once startup completes

	// Simulate startup work (e.g. warming caches, connecting to DB) in the
	// background so the server can start listening immediately.
	go func() {
		time.Sleep(3 * time.Second)
		ready.Store(true)
		log.Println("application is now ready")
	}()

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		// Liveness: if this handler runs at all, the process is alive.
		w.WriteHeader(http.StatusOK)
	})
	mux.HandleFunc("/readyz", func(w http.ResponseWriter, r *http.Request) {
		if !ready.Load() {
			http.Error(w, "not ready", http.StatusServiceUnavailable)
			return
		}
		w.WriteHeader(http.StatusOK)
	})

	srv := &http.Server{
		Addr:         ":8080",
		Handler:      mux,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 5 * time.Second,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("server failed: %v", err)
		}
	}()
	log.Println("listening on", srv.Addr)

	// Wait for termination signal, then shut down gracefully.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, syscall.SIGINT, syscall.SIGTERM)
	<-stop

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("graceful shutdown failed: %v", err)
	}
}
