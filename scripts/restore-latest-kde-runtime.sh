#!/usr/bin/env bash

set -euo pipefail

RUNTIME="org.kde.Platform//6.10"

if ! command -v flatpak >/dev/null 2>&1; then
    echo "[ERROR] Flatpak is not installed." >&2
    exit 1
fi

if ! flatpak info "$RUNTIME" >/dev/null 2>&1; then
    echo "[ERROR] Runtime $RUNTIME was not found." >&2
    exit 1
fi

if flatpak --user info "$RUNTIME" >/dev/null 2>&1; then
    flatpak --user update "$RUNTIME" -y
else
    sudo flatpak update "$RUNTIME" -y
fi

echo "[SUCCESS] $RUNTIME was updated to the latest available version."
