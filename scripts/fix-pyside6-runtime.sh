#!/usr/bin/env bash

set -euo pipefail

RUNTIME="org.kde.Platform//6.10"
APP_ID="io.github.lluciocc.Vish"
GOOD_COMMIT="a0fd8b396dc57700e0f805b2114d3925aa4aa72b10aa7b53cce4ab23c5bc68ac"

print_header() {
    echo "=========================================="
    echo " Vish Flatpak PySide6 runtime workaround"
    echo "=========================================="
    echo
}

error() {
    echo "[ERROR] $*" >&2
}

info() {
    echo "[INFO] $*"
}

success() {
    echo "[SUCCESS] $*"
}

warn() {
    echo "[WARNING] $*"
}

print_header

if ! command -v flatpak >/dev/null 2>&1; then
    error "Flatpak is not installed."
    exit 1
fi

if ! flatpak info "$RUNTIME" >/dev/null 2>&1; then
    error "Required runtime $RUNTIME was not found."
    echo
    echo "Install or update Vish from Flathub first:"
    echo "    flatpak install flathub $APP_ID"
    exit 1
fi

if ! flatpak info "$APP_ID" >/dev/null 2>&1; then
    error "Application $APP_ID is not installed."
    echo
    echo "Install it with:"
    echo "    flatpak install flathub $APP_ID"
    exit 1
fi

info "Applying rollback for $RUNTIME to the known working commit:"
echo "$GOOD_COMMIT"
echo

if flatpak --user info "$RUNTIME" >/dev/null 2>&1; then
    info "Detected user installation of $RUNTIME."
    flatpak --user update \
        --commit="$GOOD_COMMIT" \
        "$RUNTIME" \
        -y
else
    info "Detected system installation of $RUNTIME. Administrator privileges may be required."
    sudo flatpak update \
        --commit="$GOOD_COMMIT" \
        "$RUNTIME" \
        -y
fi

echo
info "Testing PySide6 imports inside the Vish Flatpak environment..."

if flatpak run --command=python3 "$APP_ID" \
    -c "from PySide6.QtCore import Qt; from PySide6.QtGui import QGuiApplication; print('PySide6 OK')" >/dev/null 2>&1
then
    success "PySide6 loaded successfully."
    echo
    echo "You can now launch Vish with:"
    echo "    flatpak run $APP_ID"
else
    warn "The rollback was applied, but the PySide6 import test still failed."
    warn "There may be another issue besides the KDE Flatpak runtime."
    echo
    echo "Try running the test manually to inspect the full error:"
    echo "    flatpak run --command=python3 $APP_ID -c \"from PySide6.QtCore import Qt; from PySide6.QtGui import QGuiApplication; print('PySide6 OK')\""
    exit 1
fi
