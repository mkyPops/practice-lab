// Package main implements a lightweight structured logger that emits
// newline-delimited JSON records containing a level, timestamp, message,
// and any number of arbitrary key/value fields. It is safe for concurrent use.
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

// String returns the lowercase name of the level, used in JSON output.
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

// Field is a single key/value pair attached to a log entry.
type Field struct {
	Key   string
	Value interface{}
}

// F is a convenience constructor for a Field.
func F(key string, value interface{}) Field {
	return Field{Key: key, Value: value}
}

// Logger writes structured JSON log lines to an underlying writer.
type Logger struct {
	out      io.Writer
	mu       sync.Mutex
	minLevel Level
}

// New creates a Logger that writes to out, filtering out entries below minLevel.
func New(out io.Writer, minLevel Level) *Logger {
	return &Logger{out: out, minLevel: minLevel}
}

// log builds the JSON record and writes it atomically.
func (l *Logger) log(level Level, msg string, fields ...Field) {
	if level < l.minLevel {
		return
	}
	// Pre-size the map for the standard fields plus any extras.
	entry := make(map[string]interface{}, len(fields)+3)
	entry["level"] = level.String()
	entry["time"] = time.Now().UTC().Format(time.RFC3339Nano)
	entry["msg"] = msg
	for _, f := range fields {
		entry[f.Key] = f.Value
	}

	data, err := json.Marshal(entry)
	if err != nil {
		// Fall back to a minimal error record rather than dropping the log silently.
		data, _ = json.Marshal(map[string]string{
			"level": Error.String(),
			"msg
