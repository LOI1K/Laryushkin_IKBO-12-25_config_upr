
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from src.main import execute_line
from src.vfs import VirtualFileSystem


VFS_PATH = (
    Path(__file__).resolve().parents[1] / "vfs_examples" / "nested"
)

FILE_PATH = "/level1/level2/level3/deep.txt"


class TestStage5(unittest.TestCase):
    """Test chmod and help commands."""

    def setUp(self):
        """Load the virtual filesystem."""
        self.vfs = VirtualFileSystem(VFS_PATH)

    def run_command(self, command):
        """Execute a command and capture its output."""
        output = StringIO()

        with redirect_stdout(output):
            running = execute_line(command, self.vfs)

        self.assertTrue(running)
        return output.getvalue()

    def test_chmod_file(self):
        """Test changing permissions of a virtual file."""
        result = self.run_command(
            "chmod 600 level1/level2/level3/deep.txt"
        )
        self.assertEqual(result, "")
        self.assertEqual(self.vfs.permissions[FILE_PATH], 0o600)

    def test_chmod_directory(self):
        """Test changing permissions of a directory."""
        self.run_command("chmod 755 level1")
        self.assertEqual(self.vfs.permissions["/level1"], 0o755)

    def test_chmod_relative_path(self):
        """Test chmod with a relative path."""
        self.run_command("cd level1/level2/level3")
        self.run_command("chmod 600 deep.txt")
        self.assertEqual(self.vfs.permissions[FILE_PATH], 0o600)

    def test_chmod_invalid_mode(self):
        """Test rejecting an invalid octal mode."""
        result = self.run_command("chmod 888 level1")
        self.assertIn("Ошибка", result)

    def test_chmod_missing_file(self):
        """Test chmod on a nonexistent file."""
        result = self.run_command("chmod 600 missing.txt")
        self.assertIn("Ошибка", result)

    def test_chmod_no_arguments(self):
        """Test chmod without arguments."""
        result = self.run_command("chmod")
        self.assertIn("Ошибка", result)

    def test_chmod_extra_arguments(self):
        """Test chmod with too many arguments."""
        result = self.run_command("chmod 600 level1 extra")
        self.assertIn("Ошибка", result)

    def test_chmod_without_vfs(self):
        """Test chmod without a loaded VFS."""
        output = StringIO()

        with redirect_stdout(output):
            running = execute_line("chmod 600 file.txt")

        self.assertTrue(running)
        self.assertIn("Ошибка", output.getvalue())

    def test_disk_unchanged(self):
        """Test that chmod does not modify the real file."""
        real_file = VFS_PATH / "level1/level2/level3/deep.txt"
        before = real_file.stat().st_mode & 0o777

        self.run_command(
            "chmod 600 level1/level2/level3/deep.txt"
        )

        after = real_file.stat().st_mode & 0o777
        self.assertEqual(before, after)
        self.assertEqual(self.vfs.permissions[FILE_PATH], 0o600)

    def test_help(self):
        """Test displaying all supported commands."""
        result = self.run_command("help")

        for command in (
            "ls", "cd", "echo", "head",
            "who", "chmod", "help", "exit",
        ):
            self.assertIn(f"{command}:", result)

    def test_help_invalid_arguments(self):
        """Test rejecting arguments for help."""
        result = self.run_command("help test")
        self.assertIn("Ошибка", result)
