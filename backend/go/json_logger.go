// Package main implements a lightweight structured JSON logger.
// Each log entry is emitted as a single JSON line containing a level,
// an RFC3339Nano timestamp, a message, and any arbitrary caller-supplied
// fields. The logger is safe for concurrent use.
package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"sync"
	"time"
)

// Level represents the severity of a log entry.
type Level int

const (
	Debug Level = iota
	Info
	Warn
	Error
)

func (l Level) String() string {
	switch l {
	case Debug:
		return "debug"
	case Info:
		return "info"
	case Warn:
		return "warn"
	case Error:
		return "error"
	default:
		return "unknown"
	}
}

// Logger writes structured JSON log lines to an output writer.
type Logger struct {
	mu     sync.Mutex
	out    io.Writer
	level  Level
	fields map[string]interface{}
}

// NewLogger creates a Logger writing to out, filtering entries below minLevel.
func NewLogger(out io.Writer, minLevel Level) *Logger {
	return &Logger{out: out, level: minLevel, fields: map[string]interface{}{}}
}

// With returns a new Logger that includes the given fields on every entry,
// in addition to any fields already attached to the parent logger.
func (l *Logger) With(fields map[string]interface{}) *Logger {
	merged := make(map[string]interface{}, len(l.fields)+len(fields))
	for k, v := range l.fields {
		merged[k] = v
	}
	for k, v := range fields {
		merged[k] = v
	}
	return &Logger{out: l.out, level: l.level, fields: merged}
}

// log builds and writes a single JSON line for the given entry.
func (l *Logger) log(level Level, msg string, fields map[string]interface{}) {
	if level < l.level {
		return // below configured threshold, skip
	}
	entry := make(map[string]interface{}, len(l.fields)+len(fields)+3)
	for k, v := range l.fields {
		entry[k] = v
	}
	for k, v := range fields {
		entry[k] = v
	}
	entry["level"] = level.String()
	entry["time"] = time.Now().UTC().Format(time.RFC3339Nano)
	entry["msg"] = msg
