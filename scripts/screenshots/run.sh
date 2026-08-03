#!/usr/bin/env bash
# Regenerates the VSCode-extension screenshots used by the workshop.
#
# Builds the extension VSIX, boots code-server in Docker with the extension and
# a seeded connector workspace, then drives it with Playwright and writes PNGs
# into static/screenshots/.
#
#   ./run.sh                              # full run, uses ../../../../IdeaProjects/fortisoar-connector-vscode
#   EXT_REPO=/path/to/ext ./run.sh        # point at the extension repo explicitly
#   ./run.sh --keep                       # leave the container running to poke at
#   ./run.sh --only connector-tree        # re-shoot a single frame
#
# Why code-server: the extension is a Node-platform extension that spawns
# Python, so it cannot run in vscode.dev (webworker host, no child_process).
# code-server runs the real extension host server-side.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSHOP="$(cd "$HERE/../.." && pwd)"
EXT_REPO="${EXT_REPO:-$HOME/IdeaProjects/fortisoar-connector-vscode}"
CONTAINER="${CONTAINER:-fsr-shots}"
PORT="${PORT:-8443}"
IMAGE="fsr-workshop-code-server:latest"
OUT="$WORKSHOP/static/screenshots"
FIXTURE="${FIXTURE:-$EXT_REPO/../connector-pycharm-plugin-release.3.0.0/src/test/resources/fixtures/connectors/hello-world-1.0.1.tgz}"

KEEP=0
PASSTHRU=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep) KEEP=1; shift ;;
    *) PASSTHRU+=("$1"); shift ;;
  esac
done

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }

[[ -d "$EXT_REPO" ]] || { echo "extension repo not found: $EXT_REPO (set EXT_REPO=)" >&2; exit 1; }
[[ -f "$FIXTURE" ]]  || { echo "connector fixture not found: $FIXTURE (set FIXTURE=)" >&2; exit 1; }
command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }

step "Building the VSIX"
(cd "$EXT_REPO" && npm run package >/dev/null)
VSIX="$EXT_REPO/fortisoar-connector.vsix"
[[ -f "$VSIX" ]] || { echo "VSIX not produced at $VSIX" >&2; exit 1; }

step "Building the screenshot image (cached after the first run)"
docker build -q -t "$IMAGE" "$HERE" >/dev/null

step "Starting code-server"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" -p "$PORT:8080" "$IMAGE" \
  --auth none --bind-addr 0.0.0.0:8080 >/dev/null

# Deterministic UI: no trust prompt, fixed dark theme, no welcome tab, no
# secondary sidebar, no command center. Without these the frames differ run to
# run and carry chrome the workshop never mentions.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/settings.json" <<'JSON'
{
  "security.workspace.trust.enabled": false,
  "workbench.colorTheme": "Default Dark Modern",
  "workbench.startupEditor": "none",
  "workbench.tips.enabled": false,
  "workbench.welcomePage.walkthroughs.openOnInstall": false,
  "workbench.secondarySideBar.defaultVisibility": "hidden",
  "window.commandCenter": false,
  "workbench.layoutControl.enabled": false,
  "editor.minimap.enabled": false,
  "telemetry.telemetryLevel": "off",
  "update.mode": "none",
  "extensions.ignoreRecommendations": true,
  "chat.commandCenter.enabled": false
}
JSON
docker exec "$CONTAINER" mkdir -p /home/coder/.local/share/code-server/User
docker cp "$TMP/settings.json" "$CONTAINER:/home/coder/.local/share/code-server/User/settings.json"
# `docker cp` lands the file owned by root. code-server runs as `coder` and
# rewrites settings.json whenever it persists UI state; without this chown that
# write fails with EACCES and VSCode opens the file as a dirty editor tab with a
# "Failed to save" notification -- which then sits in the background of every
# full-frame screenshot.
docker exec -u root "$CONTAINER" \
  chown coder:coder /home/coder/.local/share/code-server/User/settings.json

step "Verifying Python (baked into the image -- see Dockerfile)"
docker exec "$CONTAINER" python3 --version

step "Installing the extension"
docker cp "$VSIX" "$CONTAINER:/tmp/fsr.vsix"
# code-server resolves ms-python.python + ms-python.debugpy (hard
# extensionDependencies) from Open VSX automatically.
docker exec "$CONTAINER" code-server --install-extension /tmp/fsr.vsix 2>&1 | grep -v Deprecation || true

step "Seeding the connector workspace"
rm -rf "$TMP/ws" && mkdir -p "$TMP/ws/.fortisoar"
tar xzf "$FIXTURE" -C "$TMP/ws"
CONNECTOR_DIR="$(find "$TMP/ws" -maxdepth 2 -name info.json -print -quit | xargs dirname)"
python3 - "$CONNECTOR_DIR" "$TMP/ws/.fortisoar/local_data.json" <<'PY'
import json, os, sys
src, out = sys.argv[1], sys.argv[2]
info = json.load(open(os.path.join(src, "info.json")))
json.dump({"connectors": [{
    "name": info["name"], "version": info["version"],
    "path": "/home/coder/project/" + os.path.basename(src),
}]}, open(out, "w"), indent=2)
PY
docker exec "$CONTAINER" mkdir -p /home/coder/project
docker cp "$TMP/ws/." "$CONTAINER:/home/coder/project/"
docker exec -u root "$CONTAINER" chown -R coder:coder /home/coder/project
docker restart "$CONTAINER" >/dev/null

step "Waiting for code-server"
for _ in $(seq 1 60); do
  if curl -sf "http://localhost:$PORT/healthz" >/dev/null 2>&1 || curl -sf "http://localhost:$PORT/" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

step "Capturing"
cd "$HERE"
[[ -d node_modules ]] || npm install
npx playwright install chromium >/dev/null 2>&1 || true
set +e
node capture.mjs --url "http://localhost:$PORT" --out "$OUT" "${PASSTHRU[@]+"${PASSTHRU[@]}"}"
RC=$?
set -e

if [[ $KEEP -eq 1 ]]; then
  echo "container left running at http://localhost:$PORT (docker rm -f $CONTAINER to stop)"
else
  docker rm -f "$CONTAINER" >/dev/null
fi
exit $RC
