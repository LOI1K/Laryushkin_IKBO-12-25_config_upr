
VFS_NAME = "my-vfs"


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


def main():
    """Run the interactive shell."""
    while True:
        try:
            user_input = input(f"{VFS_NAME}:/$ ")
        except (EOFError, KeyboardInterrupt):
            print("\nВыход из эмулятора.")
            break

        parts = user_input.split()

        if not parts:
            continue

        command = parts[0]
        arguments = parts[1:]

        if not execute_command(command, arguments):
            break


if __name__ == "__main__":
    main()
