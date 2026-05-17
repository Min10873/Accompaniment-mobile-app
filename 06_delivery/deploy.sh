#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/opt/accompaniment-app"
INCOMING_DIR="$APP_ROOT/incoming"
RELEASES_DIR="$APP_ROOT/releases"
BACKUPS_DIR="$APP_ROOT/backups"
CURRENT_LINK="$APP_ROOT/current"
VENV_DIR="$APP_ROOT/venv"
DATA_DIR="/data/accompaniment-app"
LOG_DIR="$DATA_DIR/logs"
ENV_FILE="$APP_ROOT/env"
PID_FILE="$APP_ROOT/backend.pid"
HOST="127.0.0.1"
PORT="7001"
DEPLOY_STAGING_DIR=""
BACKEND_SERVICE="accompaniment-backend.service"
SIDECAR_SERVICE="accompaniment-sidecar.service"

usage() {
  cat >&2 <<'EOF'
Usage:
  /opt/accompaniment-app/deploy.sh deploy /opt/accompaniment-app/incoming/accompaniment-app-v0.1.0.tar.gz
  /opt/accompaniment-app/deploy.sh start
  /opt/accompaniment-app/deploy.sh stop
  /opt/accompaniment-app/deploy.sh restart
  /opt/accompaniment-app/deploy.sh status
  /opt/accompaniment-app/deploy.sh rollback
EOF
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

cleanup_staging() {
  if [[ -n "${DEPLOY_STAGING_DIR:-}" ]]; then
    rm -rf "$DEPLOY_STAGING_DIR"
  fi
}

ensure_dirs() {
  mkdir -p "$INCOMING_DIR" "$RELEASES_DIR" "$BACKUPS_DIR" "$DATA_DIR/videos" "$DATA_DIR/audio" "$DATA_DIR/tasks" "$LOG_DIR"
}

version_from_package() {
  local package_name
  package_name="$(basename "$1")"
  if [[ "$package_name" =~ (v[0-9]+\.[0-9]+\.[0-9]+)\.tar\.gz$ ]]; then
    echo "${BASH_REMATCH[1]}"
    return 0
  fi
  fail "package name must end with a version like v0.1.0.tar.gz"
}

is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(cat "$PID_FILE")"
  [[ -n "$pid" ]] || return 1
  ps -p "$pid" >/dev/null 2>&1
}

stop_app() {
  if ! is_running; then
    echo "backend is not running"
    rm -f "$PID_FILE"
    return 0
  fi

  local pid
  pid="$(cat "$PID_FILE")"
  echo "stopping backend pid=$pid"
  kill "$pid"
  for _ in 1 2 3 4 5 6 7 8 9 10; do
    if ! ps -p "$pid" >/dev/null 2>&1; then
      rm -f "$PID_FILE"
      echo "backend stopped"
      return 0
    fi
    sleep 1
  done
  fail "backend did not stop after 10 seconds; inspect pid=$pid manually"
}

start_app() {
  ensure_dirs
  [[ -L "$CURRENT_LINK" ]] || fail "$CURRENT_LINK is not set; deploy a release first"
  [[ -x "$VENV_DIR/bin/python" ]] || fail "$VENV_DIR/bin/python not found"
  if is_running; then
    echo "backend already running pid=$(cat "$PID_FILE")"
    return 0
  fi
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    fail "$HOST:$PORT is already in use; do not change VPN/x-ui/xray ports"
  fi

  cd "$CURRENT_LINK/app/backend"
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
  nohup "$VENV_DIR/bin/python" -m uvicorn app.main:app --host "$HOST" --port "$PORT" > "$LOG_DIR/backend.log" 2>&1 &
  echo "$!" > "$PID_FILE"
  sleep 2
  if ! is_running; then
    rm -f "$PID_FILE"
    fail "backend failed to start; check $LOG_DIR/backend.log"
  fi
  echo "backend started pid=$(cat "$PID_FILE") url=http://$HOST:$PORT"
}

status_app() {
  local current backend_active backend_enabled sidecar_active sidecar_enabled
  current="$(readlink "$CURRENT_LINK" 2>/dev/null || true)"
  if [[ -n "$current" ]]; then
    echo "current=$current"
  else
    echo "current=(none)"
  fi

  backend_active="$(systemctl is-active "$BACKEND_SERVICE" 2>/dev/null || true)"
  backend_enabled="$(systemctl is-enabled "$BACKEND_SERVICE" 2>/dev/null || true)"
  sidecar_active="$(systemctl is-active "$SIDECAR_SERVICE" 2>/dev/null || true)"
  sidecar_enabled="$(systemctl is-enabled "$SIDECAR_SERVICE" 2>/dev/null || true)"
  echo "systemd_backend=${backend_active:-unknown}"
  echo "systemd_backend_enabled=${backend_enabled:-unknown}"
  echo "systemd_sidecar=${sidecar_active:-unknown}"
  echo "systemd_sidecar_enabled=${sidecar_enabled:-unknown}"

  if is_running; then
    echo "legacy_pid_backend=running pid=$(cat "$PID_FILE")"
  else
    echo "legacy_pid_backend=stopped"
  fi
  if [[ -f "$ENV_FILE" ]]; then
    echo "env_file=$ENV_FILE"
    grep -E '^ACCOMPANIMENT_(MOCK_PROCESSING|SIDECAR_BASE_URL|DOWNLOAD_TIMEOUT_SECONDS|FFMPEG_TIMEOUT_SECONDS)=' "$ENV_FILE" || true
  else
    echo "env_file=(none)"
    echo "ACCOMPANIMENT_MOCK_PROCESSING=(default true)"
  fi
  if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    lsof -nP -iTCP:"$PORT" -sTCP:LISTEN
  fi
}

prepare_data_link() {
  local release_dir="$1"
  local data_link="$release_dir/app/backend/app/data"
  if [[ -L "$data_link" ]]; then
    return 0
  fi
  if [[ -d "$data_link" ]]; then
    if find "$data_link" -mindepth 1 -print -quit | grep -q .; then
      fail "$data_link is non-empty; package must not contain runtime data"
    fi
    rmdir "$data_link"
  fi
  ln -s "$DATA_DIR" "$data_link"
}

deploy_package() {
  [[ $# -eq 1 ]] || fail "deploy requires package path"
  local package_path="$1"
  [[ -f "$package_path" ]] || fail "package not found: $package_path"
  ensure_dirs

  local version release_dir staging extracted previous
  version="$(version_from_package "$package_path")"
  release_dir="$RELEASES_DIR/$version"
  staging="$RELEASES_DIR/.staging-$version-$$"
  [[ ! -e "$release_dir" ]] || fail "release already exists: $release_dir"

  mkdir -p "$staging"
  DEPLOY_STAGING_DIR="$staging"
  trap cleanup_staging EXIT
  tar -xzf "$package_path" -C "$staging"
  extracted="$(find "$staging" -mindepth 1 -maxdepth 1 -type d | head -n 1)"
  [[ -n "$extracted" ]] || fail "package did not contain a top-level directory"
  mv "$extracted" "$release_dir"
  DEPLOY_STAGING_DIR=""

  prepare_data_link "$release_dir"
  "$VENV_DIR/bin/python" -m pip install -r "$release_dir/app/backend/requirements.txt"
  "$VENV_DIR/bin/python" -m pytest "$release_dir/app/backend/tests" -q

  previous="$(readlink "$CURRENT_LINK" 2>/dev/null || true)"
  if [[ -n "$previous" ]]; then
    echo "$previous" > "$BACKUPS_DIR/previous_release"
  fi
  ln -sfn "$release_dir" "$CURRENT_LINK"
  echo "deployed $version"
}

rollback_app() {
  [[ -f "$BACKUPS_DIR/previous_release" ]] || fail "no previous release recorded"
  local previous
  previous="$(cat "$BACKUPS_DIR/previous_release")"
  [[ -d "$previous" ]] || fail "previous release directory missing: $previous"
  stop_app
  ln -sfn "$previous" "$CURRENT_LINK"
  start_app
  echo "rolled back to $previous"
}

main() {
  [[ $# -ge 1 ]] || { usage; exit 2; }
  case "$1" in
    deploy)
      shift
      deploy_package "$@"
      ;;
    start)
      start_app
      ;;
    stop)
      stop_app
      ;;
    restart)
      stop_app
      start_app
      ;;
    status)
      status_app
      ;;
    rollback)
      rollback_app
      ;;
    *)
      usage
      exit 2
      ;;
  esac
}

main "$@"
