// Package main demonstrates a composable HTTP middleware chain for net/http,
// including middleware for request logging, panic recovery, and request-ID
// injection. Middlewares are combined with Chain, which applies them in the
// order given (first middleware wraps outermost).
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"log"
	"net/http"
	"time"
)

// Middleware wraps an http.Handler to produce a new http.Handler.
type Middleware func(http.Handler) http.Handler

// Chain composes multiple middlewares into a single one. The first
// middleware in the list is the outermost (runs first on the way in,
// last on the way out).
func Chain(mws ...Middleware) Middleware {
	return func(final http.Handler) http.Handler {
		for i := len(mws) - 1; i >= 0; i-- {
			final = mws[i](final)
		}
		return final
	}
}

type ctxKey string

const requestIDKey ctxKey = "requestID"

// RequestID generates a random request ID and attaches it to the request
// context and response headers for correlation purposes.
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		buf := make([]byte, 8)
		rand.Read(buf) // crypto/rand.Read never fails in practice
		id := hex.EncodeToString(buf)
		w.Header().Set("X-Request-ID", id)
		ctx := context.WithValue(r.Context(), requestIDKey, id)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// Logger logs the method, path, status, duration, and request ID for
// each request.
func Logger(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		sw := &statusWriter{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(sw, r)
		id, _ := r.Context().Value(requestIDKey).(string)
		log.Printf("[%s] %s %s -> %d (%s)", id, r.Method, r.URL.Path, sw.status, time.Since(start))
	})
}

// Recover catches panics in downstream handlers, logs them, and responds
// with 500 instead of crashing the server.
func Recover(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				log.Printf("panic recovered: %v", err)
				http.Error(w, "internal server error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	})
}

// statusWriter captures the HTTP status code written by a handler.
type statusWriter struct {
	http.ResponseWriter
	status int
}

func (sw *statusWriter) WriteHeader(code int) {
	sw.status = code
	sw.ResponseWriter.WriteHeader(code)
}

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte("hello, world"))
	})
	mux.HandleFunc("/panic", func(w http.ResponseWriter, r *http.Request) {
		panic("boom")
	})

	chain := Chain(RequestID, Logger, Recover)
	log.Fatal(http.ListenAndServe(":8080", chain(mux)))
}
