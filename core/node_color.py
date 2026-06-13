# node_color.py
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

import json
from core.debug import Info, Debug

class NodeColor:
    node_colors = {}

    @staticmethod
    def set_node_colors():
        filename = "node_colors.json"
        color_file = Info.resource_path(f"assets/models/{filename}")
        try:
            with open(color_file) as data:
                NodeColor.node_colors = json.load(data)
        except FileNotFoundError:
            Debug.Error(f"Cannot find file '{filename}'.")

    @staticmethod
    def get_color(node_type):
        color = NodeColor.node_colors.get(node_type)
        return color