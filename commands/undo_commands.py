from PySide6.QtGui import QUndoCommand


class AddNodeCommand(QUndoCommand):
    def __init__(self, view, node):
        super().__init__("Add Node")
        self.view = view
        self.graph = view.graph
        self.node = node
        self._done = False

    def redo(self):
        if not self._done:
            self.graph.add_node(self.node)
            self.view.add_node_item(self.node)
            self._done = True
            return
        self.graph.add_node(self.node)
        self.view.add_node_item(self.node)

    def undo(self):
        self.view.remove_node_item(self.node.id)


class RemoveNodeCommand(QUndoCommand):
    def __init__(self, view, node_id: str):
        super().__init__("Remove Node")
        self.view = view
        self.scene = view.scene()
        self.graph = view.graph
        self.node_id = node_id
        self.node = self.graph.nodes.get(node_id)
        self.edge_port_pairs = []
        self._captured = False

    def _capture(self):
        if self._captured or not self.node:
            return
        for port in self.node.inputs + self.node.outputs:
            for e in list(port.connected_edges):
                self.edge_port_pairs.append((e.source, e.target))
        self._captured = True

    def redo(self):
        self._capture()
        self.view._suspend_edge_undo = True
        self.view.remove_node_item(self.node_id)
        self.view._suspend_edge_undo = False

    def undo(self):
        if not self.node:
            return
        self.view._suspend_edge_undo = True
        self.graph.add_node(self.node)
        self.view.add_node_item(self.node)
        for source_port, target_port in self.edge_port_pairs:
            edge = self.graph.add_edge(source_port, target_port)
            if edge:
                self.scene.add_core_edge(edge, self.view.node_items)
        self.view._suspend_edge_undo = False


class AddEdgeCommand(QUndoCommand):
    def __init__(self, view, source_port, target_port):
        super().__init__("Add Connection")
        self.view = view
        self.scene = view.scene()
        self.graph = view.graph
        self.source_port = source_port
        self.target_port = target_port
        self.edge_id = None

    def redo(self):
        edge = self.graph.add_edge(self.source_port, self.target_port)
        if not edge:
            self.edge_id = None
            return
        self.edge_id = edge.id
        self.scene.add_core_edge(edge, self.node_items)

    def undo(self):
        if not self.edge_id:
            return
        self.graph.remove_edge(self.edge_id)
        self.view.remove_edge_item(self.edge_id)
        self.edge_id = None


class MoveNodeCommand(QUndoCommand):
    def __init__(self, view, node_id: str, old_pos, new_pos):
        super().__init__("Move Node")
        self.view = view
        self.graph = view.graph
        self.node_id = node_id
        self.old_pos = old_pos
        self.new_pos = new_pos

    def redo(self):
        self._apply(self.new_pos)

    def undo(self):
        self._apply(self.old_pos)

    def _apply(self, pos):
        node = self.graph.nodes.get(self.node_id)
        if not node:
            return
        node.x = pos.x()
        node.y = pos.y()
        item = self.view.node_items.get(self.node_id)
        if item:
            item.setPos(pos)
            self.view.graph_scene.update_edges_for_node(item)


class PasteCommand(QUndoCommand):
    def __init__(self, view, data: dict, scene_pos=None):
        super().__init__("Paste")
        self.view = view
        self.scene = view.scene()
        self.graph = view.graph
        self.node_factory = view.node_factory
        self.data = data
        self.scene_pos = scene_pos
        self.created_node_ids = []
        self.created_edge_ids = []
        self._id_map = {}

    def redo(self):
        self.created_node_ids.clear()
        self.created_edge_ids.clear()
        self._id_map.clear()

        nodes_data = self.data.get("nodes", [])
        if not nodes_data:
            return

        avg_x = sum(n.get("x", 0) for n in nodes_data) / len(nodes_data)
        avg_y = sum(n.get("y", 0) for n in nodes_data) / len(nodes_data)

        if self.scene_pos is not None:
            dx = self.scene_pos.x() - avg_x
            dy = self.scene_pos.y() - avg_y
        else:
            dx, dy = getattr(self.view, "paste_offset", (30, 30))

        for nd in nodes_data:
            node = self.node_factory(nd["type"])
            node.properties.update(nd.get("properties", {}))
            node.x = nd.get("x", 0) + dx
            node.y = nd.get("y", 0) + dy

            self.graph.add_node(node)
            self.view.add_node_item(node)

            self._id_map[nd["id"]] = node
            self.created_node_ids.append(node.id)

        for ed in self.data.get("edges", []):
            source_node = self._id_map.get(ed.get("source_node"))
            target_node = self._id_map.get(ed.get("target_node"))
            if not source_node or not target_node:
                continue

            source_i = ed.get("source_output_index")
            target_i = ed.get("target_input_index")
            if source_i is None or target_i is None:
                continue
            if source_i >= len(source_node.outputs) or target_i >= len(target_node.inputs):
                continue

            source_port = source_node.outputs[source_i]
            target_port = target_node.inputs[target_i]

            edge = self.graph.add_edge(source_port, target_port)
            if edge:
                self.scene.add_core_edge(edge, self.view.node_items)
                self.created_edge_ids.append(edge.id)

    def undo(self):
        for eid in list(self.created_edge_ids):
            self.graph.remove_edge(eid)
            self.view.remove_edge_item(eid)
        self.created_edge_ids.clear()

        for nid in list(self.created_node_ids):
            self.view.remove_node_item(nid)
        self.created_node_ids.clear()
        self._id_map.clear()


class AddCommentCommand(QUndoCommand):
    def __init__(self, view, comment_item):
        super().__init__("Add Comment")
        self.view = view
        self.scene = view.scene()
        self.comment = comment_item

    def redo(self):
        if self.comment.scene() is None:
            self.scene.addItem(self.comment)

    def undo(self):
        if self.comment.scene() is self.scene:
            self.scene.removeItem(self.comment)


class RemoveCommentCommand(QUndoCommand):
    def __init__(self, view, comment_item):
        super().__init__("Remove Comment")
        self.view = view
        self.scene = view.scene()
        self.comment = comment_item
        self.pos = comment_item.pos()

    def redo(self):
        if self.comment.scene() is self.scene:
            self.scene.removeItem(self.comment)

    def undo(self):
        self.comment.setPos(self.pos)
        self.scene.addItem(self.comment)
