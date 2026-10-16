import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.vfs import VirtualFileSystem


class TestVirtualFileSystem(unittest.TestCase):
    """Test the virtual file system."""

    def test_minimal_vfs(self):
        """Test loading a minimal VFS."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "hello.txt").write_text(
                "Hello!", encoding="utf-8"
            )

            vfs = VirtualFileSystem(root)

            self.assertEqual(vfs.summary(), (1, 1))
            self.assertEqual(vfs.files["/hello.txt"], b"Hello!")

    def test_nested_vfs(self):
        """Test loading nested directories."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            nested = root / "level1" / "level2" / "level3"
            nested.mkdir(parents=True)

            (nested / "deep.txt").write_text(
                "Deep file", encoding="utf-8"
            )

            vfs = VirtualFileSystem(root)

            self.assertEqual(vfs.summary(), (4, 1))
            self.assertIn("/level1/level2", vfs.directories)
            self.assertIn(
                "/level1/level2/level3/deep.txt",
                vfs.files
            )

    def test_binary_file(self):
        """Test loading binary data."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            data = bytes([0, 255, 10, 128])
            (root / "binary.dat").write_bytes(data)

            vfs = VirtualFileSystem(root)

            self.assertEqual(vfs.files["/binary.dat"], data)

    def test_source_unchanged(self):
        """Test that virtual changes do not affect the disk."""
        with TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "hello.txt"
            file.write_text("Original", encoding="utf-8")

            vfs = VirtualFileSystem(root)
            vfs.files["/hello.txt"] = b"Changed"
            vfs.directories.add("/new_directory")

            self.assertEqual(file.read_bytes(), b"Original")
            self.assertFalse((root / "new_directory").exists())

    def test_invalid_directory(self):
        """Test loading a nonexistent directory."""
        with TemporaryDirectory() as directory:
            root = Path(directory) / "missing"

            with self.assertRaises(ValueError):
                VirtualFileSystem(root)


if __name__ == "__main__":
    unittest.main()
