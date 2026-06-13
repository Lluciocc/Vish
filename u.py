# u.py
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import re
from pathlib import Path

HEADER_TEMPLATE = """# {filename}
#
# Copyright 2026 Lluciocc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""

def remove_existing_header(content: str) -> str:
    """
    Supprime :
    - shebang
    - ligne d'encodage
    - commentaires initiaux
    - docstring de module éventuelle
    """

    lines = content.splitlines(keepends=True)
    idx = 0

    # Shebang
    if idx < len(lines) and lines[idx].startswith("#!"):
        idx += 1

    # Encoding
    if idx < len(lines) and re.match(r"#.*coding[:=]\s*[-\w.]+", lines[idx]):
        idx += 1

    # Commentaires initiaux
    while idx < len(lines):
        stripped = lines[idx].strip()
        if stripped.startswith("#") or stripped == "":
            idx += 1
        else:
            break

    # Docstring de module
    remaining = "".join(lines[idx:]).lstrip()

    docstring_match = re.match(
        r'^(("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'))\s*',
        remaining
    )

    if docstring_match:
        remaining = remaining[docstring_match.end():]

    return remaining.lstrip("\n")


def process_file(filepath: Path):
    try:
        content = filepath.read_text(encoding="utf-8")

        body = remove_existing_header(content)

        new_content = HEADER_TEMPLATE.format(
            filename=filepath.name
        ) + body

        filepath.write_text(new_content, encoding="utf-8")

        print(f"[OK] {filepath}")

    except Exception as e:
        print(f"[ERREUR] {filepath}: {e}")


def main():
    root = Path.cwd()

    for py_file in root.rglob("*.py"):
        process_file(py_file)

    print("Terminé.")


if __name__ == "__main__":
    main()
