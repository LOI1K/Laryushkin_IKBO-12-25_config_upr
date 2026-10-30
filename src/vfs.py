
import posixpath
from pathlib import Path


class VirtualFileSystem:
    """Virtual file system stored in memory."""

    def __init__(self, root: Path):
        """Load files and directories into memory."""
        if not root.is_dir():
            raise ValueError(f"Директория VFS не найдена: {root}")

        self.name = root.resolve().name or "root"
        self.directories = {"/"}
        self.files = {}
        self.cwd = "/"
        self.permissions = {"/": root.stat().st_mode & 0o777}

        for path in root.rglob("*"):
            if path.is_symlink():
                continue

            virtual_path = "/" + path.relative_to(root).as_posix()

            if path.is_dir():
                self.directories.add(virtual_path)
                self.permissions[virtual_path] = (
                    path.stat().st_mode & 0o777
                )
            elif path.is_file():
                self.files[virtual_path] = path.read_bytes()
                self.permissions[virtual_path] = (
                    path.stat().st_mode & 0o777
                )

    def summary(self):
        """Return the number of directories and files."""
        return len(self.directories), len(self.files)

    def resolve(self, path):
        """Normalize a path inside the virtual filesystem."""
        if path.startswith("/"):
            return posixpath.normpath(path)

        return posixpath.normpath(posixpath.join(self.cwd, path))

    def change_dir(self, path="/"):
        """Change the current virtual directory."""
        target = self.resolve(path)

        if target not in self.directories:
            raise ValueError(f"cd: директория не найдена: {path}")

        self.cwd = target

    def list_dir(self, path="."):
        """Return entries of a virtual directory."""
        target = self.resolve(path)

        if target in self.files:
            return [posixpath.basename(target)]

        if target not in self.directories:
            raise ValueError(f"ls: путь не найден: {path}")

        prefix = target.rstrip("/") + "/"
        names = []

        for item in self.directories.union(self.files):
            if not item.startswith(prefix):
                continue

            name = item[len(prefix):]
            if name and "/" not in name:
                names.append(name)

        return sorted(names)

    def read_file(self, path):
        """Read a file from virtual memory."""
        target = self.resolve(path)

        if target in self.directories:
            raise ValueError(f"head: это директория: {path}")

        if target not in self.files:
            raise ValueError(f"head: файл не найден: {path}")

        return self.files[target]

    def chmod(self, path, mode):
        """Change virtual permissions without modifying the disk."""
        target = self.resolve(path)

        if target not in self.permissions:
            raise ValueError(f"chmod: путь не найден: {path}")

        self.permissions[target] = mode
