#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 v0.1.0" >&2
  exit 2
fi

VERSION="$1"
if [[ ! "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must look like v0.1.0" >&2
  exit 2
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
PACKAGE_NAME="accompaniment-app-${VERSION}.tar.gz"
PACKAGE_PATH="$DIST_DIR/$PACKAGE_NAME"
STAGING_DIR="$DIST_DIR/.staging-accompaniment-app-${VERSION}"
TOP_DIR="$STAGING_DIR/accompaniment-app-${VERSION}"

mkdir -p "$DIST_DIR"
rm -rf "$STAGING_DIR"
mkdir -p "$TOP_DIR/app" "$TOP_DIR/06_delivery"

rsync -a \
  --exclude='app/data' \
  --exclude='.pytest_cache' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$ROOT_DIR/app/backend" "$TOP_DIR/app/"
rsync -a \
  "$ROOT_DIR/app/frontend" "$TOP_DIR/app/"
if [[ -d "$ROOT_DIR/app/admin" ]]; then
  rsync -a \
    "$ROOT_DIR/app/admin" "$TOP_DIR/app/"
fi
cp "$ROOT_DIR/06_delivery/deploy.sh" "$TOP_DIR/06_delivery/deploy.sh"

tar -czf "$PACKAGE_PATH" -C "$STAGING_DIR" "accompaniment-app-${VERSION}"
rm -rf "$STAGING_DIR"

echo "$PACKAGE_PATH"
