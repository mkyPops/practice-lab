// Package main implements a small, composable HTTP middleware chain for
// net/http servers. It provides a generic Chain helper plus three ready-to-use
// middlewares: request logging, panic recovery, and request-ID injection.
package main

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"log"
	"net/http"
	"time"
)

// Middleware wraps an http.Handler to produce a new http.Handler.
type Middleware func(http.Handler) http.Handler

// Chain applies middlewares to h in order, so that mws[0] runs first
// and wraps all subsequent middlewares and the final handler.
func Chain(h http.Handler, mws ...Middleware) http.Handler {
	for i := len(mws) - 1; i >= 0; i-- {
		h = mws[i](h)
	}
	return h
}

// ctxKey avoids collisions with keys from other packages.
type ctxKey string

const requestIDKey ctxKey = "requestID"

// RequestID generates a short random ID per request and stores it in context,
// also setting it as a response header for client-side correlation.
func RequestID(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		buf := make([]byte, 8)
		if _, err := rand.Read(buf); err != nil {
			http.Error(w, "internal error", http.StatusInternalServerError)
			return
		}
		id := hex.EncodeToString(buf)
		ctx := context.WithValue(r.Context(), requestIDKey, id)
		w.Header().Set("X-Request-ID", id)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// statusRecorder captures the status code written by downstream handlers
// so Logging can report it after the handler returns.
type statusRecorder struct {
	http.ResponseWriter
	status int
}

func (sr *statusRecorder) WriteHeader(code int) {
	sr.status = code
	sr.ResponseWriter.WriteHeader(code)
}

// Logging records method, path, status code, request ID, and latency.
func Logging(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		start := time.Now()
		rec := &statusRecorder{ResponseWriter: w, status: http.StatusOK}
		next.ServeHTTP(rec, r)
		id, _ := r.Context().Value(requestIDKey).(string)
		log.Printf("id=%s method=%s path=%s status=%d duration=%s",
			id, r.Method, r.URL.Path, rec.status, time.Since(start))
	})
}

// Recovery catches panics in downstream handlers, logs them, and returns
// a 500 response instead of crashing the server.
func Recovery(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				id, _ := r.Context().Value(requestIDKey).(string)
				log.Printf("id=%s panic recovered: %v", id, err)
				http.Error(w, "internal server error", http.StatusInternalServerError)
