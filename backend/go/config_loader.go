// Package main implements a minimal environment-aware configuration loader.
// It reads a YAconfigML file into a nested map, allows environment variables
// (prefixed with APP_, using "__" as a nesting separator) to override any
// value, validates that required keys are present, and exposes typed
// accessors for retrieving values by dot-separated path.
package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"gopkg.in/yaml.v3"
)

// Config wraps the merged configuration data.
type Config struct {
	data map[string]interface{}
}

// Load reads path, applies environment overrides, and validates required keys.
func Load(path string, required []string) (*Config, error) {
	raw, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("read config: %w", err)
	}
	var tree map[string]interface{}
	if err := yaml.Unmarshal(raw, &tree); err != nil {
		return nil, fmt.Errorf("parse yaml: %w", err)
	}
	cfg := &Config{data: tree}
	cfg.applyEnvOverrides("APP_")
	for _, key := range required {
		if _, ok := cfg.lookup(key); !ok {
			return nil, fmt.Errorf("missing required config key: %s", key)
		}
	}
	return cfg, nil
}

// applyEnvOverrides scans the environment for prefixed variables and injects
// them into the config tree, e.g. APP_DATABASE__HOST -
