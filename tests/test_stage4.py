
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from src.main import execute_line
from src.vfs import VirtualFileSystem


VFS_PATH = (
    Path(__file__).resolve().parents[1] / "vfs_examples" / "nested"
)


class TestStage4(unittest.TestCase):
    """Test the commands implemented in stage four."""

    def setUp(self):
        """Load a sample virtual filesystem."""
        self.vfs = VirtualFileSystem(VFS_PATH)

    def run_command(self, command):
        """Execute a command and capture its output."""
        output = StringIO()

        with redirect_stdout(output):
            running = execute_line(command, self.vfs)

        self.assertTrue(running)
        return output.getvalue()

    def test_ls(self):
        """Test listing the root directory."""
        self.assertEqual(self.run_command("ls"), "level1\n")

    def test_ls_file(self):
        """Test listing a single virtual file."""
        result = self.run_command(
            "ls level1/level2/level3/deep.txt"
        )
        self.assertEqual(result, "deep.txt\n")

    def test_cd(self):
        """Test changing the current directory."""
        self.run_command("cd level1/level2")
        self.assertEqual(self.vfs.cwd, "/level1/level2")

    def test_cd_parent(self):
        """Test returning to a parent directory."""
        self.run_command("cd level1/level2")
        self.run_command("cd ..")
        self.assertEqual(self.vfs.cwd, "/level1")

    def test_cd_error(self):
        """Test changing to a nonexistent directory."""
        result = self.run_command("cd nonexistent")
        self.assertIn("Ошибка", result)
        self.assertEqual(self.vfs.cwd, "/")

    def test_echo(self):
        """Test printing command arguments."""
        self.assertEqual(
            self.run_command("echo Hello World"),
            "Hello World\n",
        )

    def test_head(self):
        """Test reading the beginning of a virtual file."""
        result = self.run_command(
            "head level1/level2/level3/deep.txt"
        )
        self.assertIn("Deep file", result)

    def test_head_zero(self):
        """Test requesting zero lines."""
        result = self.run_command(
            "head -n 0 level1/level2/level3/deep.txt"
        )
        self.assertEqual(result, "")

    def test_head_error(self):
        """Test reading a nonexistent file."""
        result = self.run_command("head nonexistent.txt")
        self.assertIn("Ошибка", result)

    def test_who(self):
        """Test displaying the emulator user."""
        with patch("src.main.getpass.getuser", return_value="tester"):
            result = self.run_command("who")

        self.assertEqual(result, "tester emulator\n")

    def test_who_error(self):
        """Test rejecting arguments for who."""
        result = self.run_command("who test")
        self.assertIn("Ошибка", result)
