# practice-lab

A personal, continuously-growing collection of small, working code across languages and domains — algorithms, backend patterns, QA/test-automation helpers, and infrastructure snippets.

## Why this exists

Most of my day-to-day engineering work happens in private client repositories (SQA engineering, freelance contracts), so none of it shows up on a public profile. This repo is where I keep learning in the open: real, working code across languages and topics I use or want to get sharper at.

## How it's generated

New entries are proposed by a small automation I built and maintain — it's part of the portfolio too, not something hidden behind it:

1. `topics/queue.yaml` lists concrete things to build next (e.g. "Go: bounded worker pool").
2. `scripts/generate_and_commit.py` picks the next pending item, asks the Claude API to draft it, writes it to the right folder, and updates the index below.
3. `.github/workflows/practice-generator.yml` runs that script on a schedule via GitHub Actions.
4. Every commit message names exactly what was added. No filler, no repeats — each queue item runs once.

I review new entries as they land and expand the ones worth building on further.

## Index

<!-- AUTO-GENERATED-INDEX-START -->
- [LRU cache implementation](data-structures/python/lru_cache.py) — A fixed-capacity LRU cache using an OrderedDict, with get/put in O(1).
- [bounded worker pool](backend/go/worker_pool.go) — A worker pool with a fixed goroutine count pulling jobs from a channel, with graceful shutdown via context cancellation.
<!-- AUTO-GENERATED-INDEX-END -->

## Layout

- `algorithms/<language>/...`
- `data-structures/<language>/...`
- `backend/<language>/...`
- `qa-automation/<language>/...`
- `scripts/` — the generator itself
- `topics/queue.yaml` — what's queued up next
