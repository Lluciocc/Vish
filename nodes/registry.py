NODE_REGISTRY = {}

# TODO: Add description to every node

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
