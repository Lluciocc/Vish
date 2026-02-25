from pathlib import Path
import json
from core.debug import Info

class Project:
    NAME = ""
    PATH = ""

class ProjectManager:
    MAX_RECENTS = 10

    def __init__(self):
        self.current_project_path: Path | None = None
        self.project_data: dict | None = None
        self.config_dir = Path(Info.get_config_path()).parent
        self.recents_file = self.config_dir / "recent_projects.json"

    def create_project(self, directory: Path, name: str):
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=True)

        self.project_data = {
            "name": name,
            "version": "1.0",
            "graph_file": "graph.json"
        }

        (directory / "project.json").write_text(
            json.dumps(self.project_data, indent=4)
        )

        (directory / "graph.json").write_text(
            json.dumps({
                "nodes": [    {"id": "58f0bf92-a7a0-4d1d-8f07-916fa9a6f21e","type": "start","title": "Start","x": -74.0,"y": -174.0,"properties": {},"inputs": [],
                "outputs": [
                    {
                    "id": "0d391cac-0455-43d3-84b3-c3ac042326d9",
                    "name": "Exec",
                    "type": "exec"
                    }
                ]
                },
                ],
                "edges": [],
                "comments": []
            }, indent=4)
        )

        Project.NAME = name
        Project.PATH = str(directory)
        self.current_project_path = directory
        self._add_recent(directory)

    def load_project(self, directory: Path):
        directory = directory.resolve()
        project_file = directory / "project.json"

        if not project_file.exists():
            raise FileNotFoundError("project.json not found")

        self.project_data = json.loads(project_file.read_text())
        self.current_project_path = directory
        self._add_recent(directory)

    def get_graph_path(self) -> Path:
        if not self.current_project_path or not self.project_data:
            raise RuntimeError("No project loaded")
        return self.current_project_path / self.project_data["graph_file"]

    def get_project_path(self) -> Path | None:
        return self.current_project_path

    def get_recent_projects(self) -> list[str]:
        if not self.recents_file.exists():
            return []

        try:
            data = json.loads(self.recents_file.read_text())
            return [p for p in data if Path(p).exists()]
        except Exception:
            return []

    def _add_recent(self, path: Path):
        path = str(path.resolve())

        self.config_dir.mkdir(parents=True, exist_ok=True)

        recents = self.get_recent_projects()

        if path in recents:
            recents.remove(path)

        recents.insert(0, path)
        recents = recents[:self.MAX_RECENTS]

        self.recents_file.write_text(
            json.dumps(recents, indent=4)
        )
