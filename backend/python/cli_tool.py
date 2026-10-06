#!/usr/bin/env python3
"""
A small CLI tool demonstrating argparse subcommands, JSON config loading,
coloured terminal output, and centralized error handling.

Usage:
    cli.py init --config config.json
    cli.py show --config config.json
    cli.py set --config config.json key value
"""

import argparse
import json
import sys
from pathlib import Path


class Color:
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"


def cprint(msg, color=Color.RESET):
    print(f"{color}{msg}{Color.RESET}")


def load_config(path):
    config_path = Path(path)
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in config '{path}': {exc}") from exc


def save_config(path, data):
    Path(path).write_text(json.dumps(data, indent=2))


def cmd_init(args):
    save_config(args.config, {})
    cprint(f"Initialized empty config at '{args.config}'", Color.GREEN)


def cmd_show(args):
    data = load_config(args.config)
    if not data:
        cprint("Config is empty.", Color.YELLOW)
        return
    for key, value in data.items():
        print(f"{Color.GREEN}{key}{Color.RESET} = {value}")


def cmd_set(args):
    data = load_config(args.config)
    data[args.key] = args.value
    save_config(args.config, data)
    cprint(f"Set '{args.key}' = '{args.value}'", Color.GREEN)


def build_parser():
    parser = argparse.ArgumentParser(prog="cli", description="Simple config-managing CLI tool.")
    parser.add_argument("--config", default="config.json", help="Path to config file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_init = subparsers.add_parser("init", help="Create a new empty config file")
    p_init.set_defaults(func=cmd_init)

    p_show = subparsers.add_parser("show", help="Display current config contents")
    p_show.set_defaults(func=cmd_show)

    p_set = subparsers.add_parser("set", help="Set a key/value pair in the config")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except (ValueError, OSError) as exc:
        cprint(f"Error: {exc}", Color.RED)
        sys.exit(1)


if __name__ == "__main__":
    main()
