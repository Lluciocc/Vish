# PR description

## Summary

This PR adds troubleshooting documentation and optional helper scripts for a Flatpak runtime issue that may prevent Vish from starting due to PySide6 import failures.

Users affected by the issue may see errors such as:

```text
ImportError: could not import module 'PySide6.QtGui'
```

or:

```text
ImportError: could not import module 'PySide6.QtCore'
```

## Changes

- Added `docs/troubleshooting.md`
- Added `scripts/fix-pyside6-runtime.sh`
- Added `scripts/restore-latest-kde-runtime.sh`
- Documented a temporary workaround that rolls back `org.kde.Platform//6.10` to a known working commit
- Added verification steps for PySide6 imports inside the Vish Flatpak environment
- Added instructions to revert the workaround once the upstream runtime is fixed

## Notes

This is intended as a temporary workaround for users affected by a Flatpak KDE runtime issue. It does not change Vish source code or application behavior.

Known working runtime commit:

```text
a0fd8b396dc57700e0f805b2114d3925aa4aa72b10aa7b53cce4ab23c5bc68ac
```
