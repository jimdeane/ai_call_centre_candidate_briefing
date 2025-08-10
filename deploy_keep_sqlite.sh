#!/usr/bin/env bash
set -euo pipefail

# Adjust these if needed
PROJECT="${PROJECT:-$(basename "$PWD")}"
VOLUME="${VOLUME:-${PROJECT}_questionnaire_data}"
SQLITE_GLOB="${SQLITE_GLOB:-*.sqlite*}"   # e.g. set to '*.db*' if you prefer

TMP_DIR="$(mktemp -d)"
cleanup() { rm -rf "$TMP_DIR" || true; }
trap cleanup EXIT

echo "Project: $PROJECT"
echo "Volume:  $VOLUME"
echo "Backup dir: $TMP_DIR"
echo "SQLite glob: $SQLITE_GLOB"

echo "Exporting SQLite files (if any) from volume…"
docker run --rm \
  -v "${VOLUME}:/data" \
  -v "${TMP_DIR}:/backup" \
  alpine:3.20 sh -ceu '
    set -e
    mkdir -p /backup
    found=0
    for f in /data/'"$SQLITE_GLOB"'; do
      if [ -e "$f" ]; then
        cp -a "$f" /backup/
        found=1
      fi
    done
    if [ "$found" -eq 1 ]; then
      echo "Backed up:"
      ls -lah /backup
    else
      echo "No matching SQLite files found; proceeding without a DB backup."
    fi
  '

echo "Stopping stack and removing volumes…"
docker compose down -v

echo "Recreating named volume…"
docker volume create "$VOLUME" >/dev/null

echo "Restoring SQLite files (if any) into fresh volume…"
docker run --rm \
  -v "${VOLUME}:/data" \
  -v "${TMP_DIR}:/backup" \
  alpine:3.20 sh -ceu '
    set -e
    if [ -n "$(ls -A /backup 2>/dev/null || true)" ]; then
      cp -a /backup/. /data/
      echo "Restored:"
      ls -lah /data
    else
      echo "No backup files to restore."
    fi
  '

echo "Rebuilding images…"
docker compose build

echo "Starting stack…"
docker compose up -d

echo "Done. Containers:"
docker compose ps
