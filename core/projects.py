from pathlib import Path
from datetime import datetime, timezone
import json
from core.debug import Info
from core.logger import Logger

class Project:
    NAME = ""
    PATH = ""
    LAST_MODIFIED = None

class ProjectManager:
    MAX_RECENTS = 10

    def __init__(self):
        self.current_project_path: Path | None = None
        self.project_data: dict | None = None
        self.config_dir = Path(Info.get_config_path()).parent
        self.recents_file = self.config_dir / "vish" / "recent_projects.json"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _write_project_json(self, directory: Path):
        (directory / "project.json").write_text(
            json.dumps(self.project_data, indent=4)
        )

    def create_project(self, directory: Path, name: str):
        directory = directory.resolve()
        directory.mkdir(parents=True, exist_ok=True)
        self.project_data = {
            "name": name,
            "version": "1.0",
            "graph_file": "graph.json",
            "last_modified": self._now_iso(),
        }
        self._write_project_json(directory)
        (directory / "graph.json").write_text(
            json.dumps({
                "nodes": [
                    {
                        "id": "58f0bf92-a7a0-4d1d-8f07-916fa9a6f21e",
                        "type": "start",
                        "title": "Start",
                        "x": -74.0,
                        "y": -174.0,
                        "properties": {},
                        "inputs": [],
                        "outputs": [
                            {
                                "id": "0d391cac-0455-43d3-84b3-c3ac042326d9",
                                "name": "Exec",
                                "type": "exec",
                            }
                        ],
                    }
                ],
                "edges": [],
                "comments": [],
            }, indent=4)
        )
        Project.NAME = name
        Project.PATH = str(directory)
        Project.LAST_MODIFIED = self.project_data["last_modified"]
        self.current_project_path = directory
        self._add_recent(directory)

    def load_project(self, directory: Path):
        directory = directory.resolve()
        project_file = directory / "project.json"
        if not project_file.exists():
            raise FileNotFoundError("project.json not found")
        self.project_data = json.loads(project_file.read_text())
        Project.NAME = self.project_data.get("name", directory.name)
        Project.PATH = str(directory)
        Project.LAST_MODIFIED = self.project_data.get("last_modified")
        self.current_project_path = directory
        self._add_recent(directory)

    def touch_project(self):
        if not self.current_project_path or not self.project_data:
            return
        self.project_data["last_modified"] = self._now_iso()
        Project.LAST_MODIFIED = self.project_data["last_modified"]
        self._write_project_json(self.current_project_path)

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
        
    def remove_project(self, path: Path):
        path = str(path.resolve())
        recents = self.get_recent_projects()
        if path in recents:
            recents.remove(path)
            self.recents_file.write_text(json.dumps(recents, indent=4))

    def _add_recent(self, path: Path):
        path = str(path.resolve())

        self.recents_file.parent.mkdir(parents=True, exist_ok=True)

        recents = self.get_recent_projects()
        if path in recents:
            recents.remove(path)

        recents.insert(0, path)
        recents = recents[:self.MAX_RECENTS]

        self.recents_file.write_text(json.dumps(recents, indent=4))

    def rename_project(self, old_path: Path, new_name: str) -> Path:
        old_path = old_path.resolve()
        new_path = old_path.parent / new_name

        if not old_path.exists():
            raise FileNotFoundError("Project folder not found")

        if new_path.exists():
            raise FileExistsError("A project with this name already exists")

        if any(c in new_name for c in r'<>:"/\|?*'):
            raise ValueError("Invalid project name")

        if self.current_project_path and self.current_project_path.resolve() == old_path:
            raise RuntimeError("Cannot rename currently opened project")

        renamed = False

        try:
            old_path.rename(new_path) # Rename the folder
            renamed = True

            # Update in project.json 
            project_file = new_path / "project.json"
            if project_file.exists():
                data = json.loads(project_file.read_text())
                data["name"] = new_name
                project_file.write_text(json.dumps(data, indent=4))

            # Update in recents
            if self.recents_file.exists():
                recents = json.loads(self.recents_file.read_text())
            else:
                recents = []
            recents = [str(new_path) if p == str(old_path) else p for p in recents]
            self.recents_file.write_text(json.dumps(recents, indent=4))

            return new_path

        except Exception as e: # were trying to rename but something went wrong, attempt to rollback if we already renamed
            if renamed:
                try:
                    new_path.rename(old_path)
                except Exception:
                    Logger.LogError(f"Failed to rollback project rename from {new_path} to {old_path} after an error occurred: {e}")
                    raise RuntimeError(
                        f"Rename failed and rollback also failed.\nOriginal error: {e}"
                    )
            raise e