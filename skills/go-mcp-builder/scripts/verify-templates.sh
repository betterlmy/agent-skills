#!/usr/bin/env bash
set -euo pipefail

skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

cp "$skill_dir"/templates/go.mod "$tmp_dir"/
cp "$skill_dir"/templates/*.go "$tmp_dir"/

cd "$tmp_dir"
gofmt -w ./*.go
go mod tidy
go test ./...
go vet ./...
