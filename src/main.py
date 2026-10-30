
import argparse
import sys
import getpass
from pathlib import Path
from src.vfs import VirtualFileSystem

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


def run_ls(vfs, arguments):
    """List files in the virtual directory."""
    if len(arguments) > 1:
        print("Ошибка: ls принимает не более одного аргумента.")
        return

    path = arguments[0] if arguments else "."

    try:
        for name in vfs.list_dir(path):
            print(name)
    except ValueError as error:
        print(f"Ошибка: {error}")


def run_cd(vfs, arguments):
    """Change the current virtual directory."""
    if len(arguments) > 1:
        print("Ошибка: cd принимает не более одного аргумента.")
        return

    path = arguments[0] if arguments else "/"

    try:
        vfs.change_dir(path)
    except ValueError as error:
        print(f"Ошибка: {error}")


def shell_prompt(vfs_name, vfs):
    """Build the shell prompt."""
    current_dir = vfs.cwd if vfs is not None else "/"
    return f"{vfs_name}:{current_dir}$ "


def run_head(vfs, arguments):
    """Print the first lines of a virtual file."""
    if len(arguments) == 1:
        count = 10
        path = arguments[0]
    elif len(arguments) == 3 and arguments[0] == "-n":
        try:
            count = int(arguments[1])
        except ValueError:
            print("Ошибка: head: количество строк должно быть числом.")
            return

        if count < 0:
            print("Ошибка: head: число строк не может быть отрицательным.")
            return

        path = arguments[2]
    else:
        print("Ошибка: использование: head [-n число] файл")
        return

    try:
        data = vfs.read_file(path).decode("utf-8", errors="replace")
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    output = "".join(data.splitlines(keepends=True)[:count])

    if output:
        print(output, end="" if output.endswith("\n") else "\n")


def run_navigation(command, arguments, vfs):
    """Execute ls or cd depending on the command."""
    if vfs is None:
        print(f"Команда: {command}")
        print(f"Аргументы: {arguments}")
    elif command == "ls":
        run_ls(vfs, arguments)
    else:
        run_cd(vfs, arguments)


def execute_command(command, arguments, vfs=None):
    """Execute a shell command."""
    if command == "exit":
        if arguments:
            print("Ошибка: exit не принимает аргументы.")
            return True

        print("Выход из эмулятора.")
        return False

    if command in ("ls", "cd"):
        run_navigation(command, arguments, vfs)
    elif command == "echo":
        print(" ".join(arguments))
    elif command == "head":
        if vfs is None:
            print("Ошибка: VFS не загружена.")
        else:
            run_head(vfs, arguments)
    elif command == "who":
        if arguments:
            print("Ошибка: who не принимает аргументы.")
        else:
            print(f"{getpass.getuser()} emulator")
    else:
        print(f"Ошибка: неизвестная команда '{command}'")

    return True


def execute_line(line, vfs=None):
    """Parse and execute one input line."""
    parts = line.split()

    if not parts:
        return True

    return execute_command(parts[0], parts[1:], vfs)


def run_script(path, vfs_name=VFS_NAME, vfs=None):
    """Execute commands from a startup script."""
    try:
        with path.open(encoding="utf-8") as script:
            for raw_line in script:
                line = raw_line.strip()

                if not line or line.startswith("#"):
                    continue

                print(f"{shell_prompt(vfs_name, vfs)}{line}")

                if not execute_line(line, vfs):
                    return False

    except OSError as error:
        print(f"Ошибка чтения скрипта: {error}")

    return True


def main(argv=()):
    """Start the shell emulator."""
    args = parse_arguments(argv)

    print(f"VFS: {args.vfs or 'не указана'}")
    print(f"Стартовый скрипт: {args.script or 'не указан'}")

    vfs = None
    vfs_name = VFS_NAME

    if args.vfs:
        try:
            vfs = VirtualFileSystem(args.vfs)
        except (OSError, ValueError) as error:
            print(f"Ошибка загрузки VFS: {error}")
            return

        vfs_name = vfs.name
        directories, files = vfs.summary()
        print(f"VFS загружена: {directories} директории, "
              f"{files} файлов.")

    if args.script and not run_script(args.script, vfs_name, vfs):
        return

    while True:
        try:
            user_input = input(shell_prompt(vfs_name, vfs))
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из эмулятора.")
            break

        if not execute_line(user_input, vfs):
            break


if __name__ == "__main__":
    main(sys.argv[1:])
