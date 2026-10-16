
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path
from tempfile import TemporaryDirectory

from src.main import (
  execute_command,
  main,
  parse_arguments,
  run_script
)


class TestShell(unittest.TestCase):
    """Test the shell emulator."""

    def run_command(self, command, arguments):
        """Execute a command and capture its output."""
        output = io.StringIO()

        with redirect_stdout(output):
            running = execute_command(command, arguments)

        return running, output.getvalue()

    def test_ls(self):
        """Test the ls command."""
        running, output = self.run_command("ls", ["documents"])
        self.assertTrue(running)
        self.assertIn("Команда: ls", output)
        self.assertIn("documents", output)

    def test_cd(self):
        """Test the cd command."""
        running, output = self.run_command("cd", ["home"])
        self.assertTrue(running)
        self.assertIn("Команда: cd", output)
        self.assertIn("home", output)

    def test_unknown_command(self):
        """Test handling an unknown command."""
        running, output = self.run_command("unknown", [])
        self.assertTrue(running)
        self.assertIn("Ошибка: неизвестная команда", output)

    def test_exit_with_arguments(self):
        """Test rejecting arguments for exit."""
        running, output = self.run_command("exit", ["123"])
        self.assertTrue(running)
        self.assertIn("Ошибка", output)

    def test_exit(self):
        """Test exiting the emulator."""
        running, output = self.run_command("exit", [])
        self.assertFalse(running)
        self.assertIn("Выход из эмулятора", output)

    def test_repl_parser(self):
        """Test parsing commands in the REPL."""
        output = io.StringIO()
        commands = ["ls documents photos", "", "exit"]

        with patch("builtins.input", side_effect=commands):
            with redirect_stdout(output):
                main()

        self.assertIn("['documents', 'photos']", output.getvalue())

    def test_parse_arguments(self):
        """Test command-line parameters."""
        args = parse_arguments([
            "--vfs", "virtual",
            "--script", "demo.txt"
        ])

        self.assertEqual(args.vfs, Path("virtual"))
        self.assertEqual(args.script, Path("demo.txt"))

    def test_script_continues_after_error(self):
        """Test skipping invalid commands."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "demo.txt"
            path.write_text(
                "ls first\nunknown\ncd second\n",
                encoding="utf-8"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                running = run_script(path)

        self.assertTrue(running)
        self.assertIn("неизвестная команда", output.getvalue())
        self.assertIn("Команда: cd", output.getvalue())

    def test_script_exit(self):
        """Test stopping a script with exit."""
        with TemporaryDirectory() as directory:
            path = Path(directory) / "demo.txt"
            path.write_text(
                "ls first\nexit\nls second\n",
                encoding="utf-8"
            )

            output = io.StringIO()
            with redirect_stdout(output):
                running = run_script(path)

        self.assertFalse(running)
        self.assertNotIn("ls second", output.getvalue())


if __name__ == "__main__":
    unittest.main()
