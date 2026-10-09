
import argparse
import sys
from pathlib import Path

VFS_NAME = "my-vfs"


def parse_arguments(argv):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки UNIX"
    )
    parser.add_argument(
        "--vfs",
        type=Path,
        help="Путь к директории VFS"
    )
    parser.add_argument(
        "--script",
        type=Path,
        help="Путь к стартовому скрипту",
    )
    return parser.parse_args(argv)


def execute_command(command, arguments):
    """Execute a shell command."""
    if command == "exit":
        if arguments:
            print("Ошибка: exit не принимает аргументы.")
            return True

        print("Выход из эмулятора.")
        return False

    if command in ("ls", "cd"):
        print(f"Команда: {command}")
        print(f"Аргументы: {arguments}")
    else:
        print(f"Ошибка: неизвестная команда '{command}'")

    return True


def execute_line(line):
    """Parse and execute one input line."""
    parts = line.split()

    if not parts:
        return True

    return execute_command(parts[0], parts[1:])


def run_script(path):
    """Execute commands from a startup script."""
    try:
        with path.open(encoding="utf-8") as script:
            for raw_line in script:
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                print(f"{VFS_NAME}:/$ {line}")

                if not execute_line(line):
                    return False

    except OSError as error:
        print(f"Ошибка чтения скрипта: {error}")

    return True


def main(argv=()):
    """Start the shell emulator."""
    args = parse_arguments(argv)

    print(f"VFS: {args.vfs or 'не указана'}")
    print(f"Стартовый скрипт: {args.script or 'не указан'}")

    if args.script and not run_script(args.script):
        return

    while True:
        try:
            user_input = input(f"{VFS_NAME}:/$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из эмулятора.")
            break

        if not execute_line(user_input):
            break


if __name__ == "__main__":
    main(sys.argv[1:])
