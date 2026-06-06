# Troubleshooting

## Flatpak: `ImportError: could not import module 'PySide6.QtGui'`

### Symptoms

When launching Vish through Flatpak, the application may fail to start with an error similar to:

```text
Traceback (most recent call last):
  File "/app/share/vish/main.py", line 11, in <module>
    from PySide6.QtWidgets import ...
ImportError: could not import module 'PySide6.QtGui'
```

In some cases, the error may reference `PySide6.QtCore` instead:

```text
ImportError: could not import module 'PySide6.QtCore'
```

The problem can also be reproduced with:

```bash
flatpak run --command=python3 io.github.lluciocc.Vish \
  -c "from PySide6.QtGui import QGuiApplication"
```

### Cause

This issue is not caused by Vish itself, Hyprland, or a specific Linux distribution.

The failure appears to be related to a problematic version of the Flatpak KDE runtime `org.kde.Platform//6.10`, which can prevent PySide6 modules such as `PySide6.QtCore` and `PySide6.QtGui` from loading correctly inside the Flatpak environment.

Because Vish uses PySide6, the application may fail before the main window is created.

### Workaround

A temporary workaround is to roll back the KDE runtime to a known working commit:

```text
a0fd8b396dc57700e0f805b2114d3925aa4aa72b10aa7b53cce4ab23c5bc68ac
```

Run:

```bash
flatpak update \
  --commit=a0fd8b396dc57700e0f805b2114d3925aa4aa72b10aa7b53cce4ab23c5bc68ac \
  org.kde.Platform//6.10
```

Then launch Vish again:

```bash
flatpak run io.github.lluciocc.Vish
```

### Automated workaround script

This repository includes an optional helper script:

```bash
scripts/fix-pyside6-runtime.sh
```

It checks whether Flatpak, Vish, and the required KDE runtime are available, applies the rollback, and verifies that PySide6 can be imported successfully.

Usage:

```bash
chmod +x scripts/fix-pyside6-runtime.sh
./scripts/fix-pyside6-runtime.sh
```

### Verifying the fix

After applying the workaround, this command should run without errors:

```bash
flatpak run --command=python3 io.github.lluciocc.Vish \
  -c "from PySide6.QtCore import Qt; from PySide6.QtGui import QGuiApplication; print('PySide6 OK')"
```

Expected output:

```text
PySide6 OK
```

If the command succeeds, Vish should launch normally.

### Reverting the workaround

Once the KDE Flatpak runtime is fixed upstream, return to the latest runtime version with:

```bash
flatpak update org.kde.Platform//6.10
```

Or use the included helper script:

```bash
chmod +x scripts/restore-latest-kde-runtime.sh
./scripts/restore-latest-kde-runtime.sh
```

### Affected systems

Since the issue originates from the Flatpak runtime, it may affect any Linux distribution using Vish through Flatpak with the affected KDE runtime, including but not limited to:

- Arch Linux
- EndeavourOS
- CachyOS
- Manjaro
- Fedora
- Linux Mint
- Ubuntu
- Debian
- openSUSE

### Notes for maintainers

This is intended as a temporary workaround, not a permanent application-level fix. Once the affected runtime is fixed upstream, users should update `org.kde.Platform//6.10` normally and stop using the pinned commit.
