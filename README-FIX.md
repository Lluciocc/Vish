# Vish Flatpak PySide6 Runtime Workaround

This PR adds troubleshooting documentation and helper scripts for a Flatpak runtime issue that can prevent Vish from starting with PySide6 import errors.

## Added files

```text
docs/troubleshooting.md
scripts/fix-pyside6-runtime.sh
scripts/restore-latest-kde-runtime.sh
```

## What this fixes

Some users may see Vish fail to start with errors like:

```text
ImportError: could not import module 'PySide6.QtGui'
```

or:

```text
ImportError: could not import module 'PySide6.QtCore'
```

The documented workaround rolls back `org.kde.Platform//6.10` to a known working commit.

## Script usage

Apply the workaround:

```bash
chmod +x scripts/fix-pyside6-runtime.sh
./scripts/fix-pyside6-runtime.sh
```

Restore the latest KDE runtime after the upstream issue is fixed:

```bash
chmod +x scripts/restore-latest-kde-runtime.sh
./scripts/restore-latest-kde-runtime.sh
```
