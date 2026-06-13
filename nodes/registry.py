# registry.py
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

NODE_REGISTRY = {}

def register_node(node_type: str, *, label=None, category="Other", description=""):
    def decorator(cls):
        NODE_REGISTRY[node_type] = {
            "class": cls,
            "label": label or cls.__name__,
            "category": category,
            "description": description,
        }
        return cls
    return decorator

def create_node(node_type):
    entry = NODE_REGISTRY.get(node_type)
    if not entry:
        raise ValueError(f"Unknown node type: {node_type}")
    return entry["class"]()
