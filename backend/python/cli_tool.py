#!/usr/bin/env python3
"""
A small CLI tool ("confman") for managing a JSON config file.

Subcommands:
    init          create a new config file
    get <key>     print the value of a key
    set <key> <value>  set a key to a value
    list          list all key/value pairs

Config is stored as JSON at ~/.confman.json unless --config is given.
"""

import argparse
import json
import sys
from pathlib import Path


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: {exc}") from exc


def save_config(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True))


def cmd_init(args):
    if args.config.exists() and not args.force:
        raise RuntimeError(f"{args.config} already exists (use --force to overwrite)")
    save_config(args.config, {})
    print(f"{Colors.GREEN}Initialized config at {args.config}{Colors.RESET}")


def cmd_get(args):
    data = load_config(args.config)
    if args.key not in data:
        raise RuntimeError(f"key '{args.key}' not found")
    print(data[args.key])


def cmd_set(args):
    data = load_config(args.config)
    data[args.key] = args.value
    save_config(args.config, data)
    print(f"{Colors.GREEN}Set {args.key} = {args.value}{Colors.RESET}")


def cmd_list(args):
    data = load_config(args.config)
    if not data:
        print(f"{Colors.YELLOW}(empty config){Colors.RESET}")
        return
    for key, value in sorted(data.items()):
        print(f"{Colors.GREEN}{key}{Colors.RESET} = {value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="confman", description="Manage a JSON config file.")
    parser.add_argument(
        "--config", type=Path, default=Path.home() / ".confman.json", help="path to config file"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="create a new config file")
    p_init.add_argument("--force", action="store_true", help="overwrite existing config")
    p_init.set_defaults(func=cmd_init)

    p_get = sub.add_parser("get", help="get a value")
    p_get.add_argument("key")
    p_get.set_defaults(func=cmd_get)

    p_set = sub.add_parser("set", help="set a value")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_set.set_defaults(func=cmd_set)

    p_list = sub.add_parser("list", help="list all values")
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except RuntimeError as exc:
        print(f"{Colors.RED}Error: {exc}{Colors.RESET}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"{Colors.RED}I/O error: {exc}{Colors.RESET}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
