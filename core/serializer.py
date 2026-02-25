import json
from typing import Dict, Any
from .graph import Graph, Node, Port

class Serializer:
    VERSION = "0.0.0.beta"

    def __init__(self, graph: Graph):
        self.graph = graph
        
    
    @staticmethod
    def serialize(graph: Graph, graph_view) -> str:
        data = {
            "version": Serializer.VERSION,
            "nodes": [],
            "edges": [],
            "comments": []
        }
        
        for node in graph.nodes.values():
            node_data = {
                "id": node.id,
                "type": node.node_type,
                "title": node.title,
                "x": node.x,
                "y": node.y,
                "properties": node.properties,
                "inputs": [{"id": p.id, "name": p.name, "type": p.port_type.value} for p in node.inputs],
                "outputs": [{"id": p.id, "name": p.name, "type": p.port_type.value} for p in node.outputs]
            }
            data["nodes"].append(node_data)
        
        for edge in graph.edges.values():
            edge_data = {
                "id": edge.id,
                "source": edge.source.id,
                "target": edge.target.id
            }
            data["edges"].append(edge_data)

        for item in graph_view.graph_scene.items():
            if item.__class__.__name__ == "CommentBoxItem":
                r = item.rect()
                c = item.brush().color()
                data["comments"].append({
                    "x": item.pos().x(),
                    "y": item.pos().y(),
                    "w": r.width(),
                    "h": r.height(),
                    "title": item.title_item.toPlainText(),
                    "color": [c.red(), c.green(), c.blue(), c.alpha()],
                    "locked": item.locked
                })
        
        return json.dumps(data, indent=2)
    
    @staticmethod
    def deserialize(json_str: str, node_factory) -> Graph:
        data = json.loads(json_str)
        graph = Graph()
        port_map = {}

        for node_data in data["nodes"]:
            node = node_factory.create_node(node_data["type"])
            if node is None:
                raise ValueError((f"Unknown node type: {node_data['type']}", node_data['type']))
            
            node.id = node_data["id"]
            node.title = node_data["title"]
            node.x = node_data["x"]
            node.y = node_data["y"]
            node.properties = node_data.get("properties", {})
            graph.add_node(node)

            for saved, port in zip(node_data.get("inputs", []), node.inputs):
                port.id = saved["id"]
                port_map[port.id] = port

            for saved, port in zip(node_data.get("outputs", []), node.outputs):
                port.id = saved["id"]
                port_map[port.id] = port

        for edge_data in data["edges"]:
            source = port_map.get(edge_data["source"])
            target = port_map.get(edge_data["target"])
            if source and target:
                graph.add_edge(source, target)
        return graph, data.get("comments", [])

    def serialize_node(self, node):
        return {
            "id": node.id,
            "type": node.node_type,
            "x": node.x,
            "y": node.y,
            "properties": dict(node.properties),
            "inputs": [p.id for p in node.inputs],
            "outputs": [p.id for p in node.outputs],
        }

    def serialize_edge(self, edge):
        src_node = edge.source.node
        tgt_node = edge.target.node

        src_out_index = src_node.outputs.index(edge.source)
        tgt_in_index = tgt_node.inputs.index(edge.target)

        return {
            "source_node": src_node.id,
            "source_output_index": src_out_index,
            "target_node": tgt_node.id,
            "target_input_index": tgt_in_index,
        }


    def serialize_subgraph(self, nodes):
        node_ids = {n.id for n in nodes}
        data = {"nodes": [], "edges": []}

        for node in nodes:
            data["nodes"].append(self.serialize_node(node))

        for edge in self.graph.edges.values():
            if (
                edge.source.node.id in node_ids
                and edge.target.node.id in node_ids
            ):
                data["edges"].append(self.serialize_edge(edge))

        return data