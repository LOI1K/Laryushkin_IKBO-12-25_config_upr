
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from src.main import execute_command, main


class TestShell(unittest.TestCase):
    """Test the shell emulator."""

    def run_command(self, command, arguments):
        """Execute a command and capture its output."""
        output = io.StringIO()

        with redirect_stdout(output):
            running = execute_command(command, arguments)

        return running, output.getvalue()

    def test_ls(self):
        running, output = self.run_command("ls", ["documents"])
        self.assertTrue(running)
        self.assertIn("Команда: ls", output)
        self.assertIn("documents", output)

    def test_cd(self):
        running, output = self.run_command("cd", ["home"])
        self.assertTrue(running)
        self.assertIn("Команда: cd", output)
        self.assertIn("home", output)

    def test_unknown_command(self):
        running, output = self.run_command("unknown", [])
        self.assertTrue(running)
        self.assertIn("Ошибка: неизвестная команда", output)

    def test_exit_with_arguments(self):
        running, output = self.run_command("exit", ["123"])
        self.assertTrue(running)
        self.assertIn("Ошибка", output)

    def test_exit(self):
        running, output = self.run_command("exit", [])
        self.assertFalse(running)
        self.assertIn("Выход из эмулятора", output)

    def test_repl_parser(self):
        output = io.StringIO()
        commands = ["ls documents photos", "", "exit"]

        with patch("builtins.input", side_effect=commands):
            with redirect_stdout(output):
                main()

        self.assertIn("['documents', 'photos']", output.getvalue())


if __name__ == "__main__":
    unittest.main()
