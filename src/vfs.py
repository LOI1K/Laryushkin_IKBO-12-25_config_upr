from pathlib import Path


class VirtualFileSystem:
    """Virtual file system stored in memory."""

    def __init__(self, root: Path):
        """Load files and directories into memory."""
        if not root.is_dir():
            raise ValueError(f"Директория VFS не найдена: {root}")

        self.name = root.name
        self.directories = {"/"}
        self.files = {}

        for path in root.rglob("*"):
            if path.is_symlink():
                continue

            virtual_path = "/" + path.relative_to(root).as_posix()

            if path.is_dir():
                self.directories.add(virtual_path)
            elif path.is_file():
                self.files[virtual_path] = path.read_bytes()

    def summary(self):
        """Return the number of directories and files."""
        return len(self.directories), len(self.files)