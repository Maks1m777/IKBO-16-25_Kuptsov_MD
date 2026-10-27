import sys
import shlex

VFS_NAME = "VFS"

# Приглашение командной строки
PROMPT = f"{VFS_NAME}$ "


def parse_command(line: str):
    line = line.strip()
    if not line:
        return None, []

    parts = shlex.split(line)
    command = parts[0]
    args = parts[1:]
    return command, args


def cmd_ls(args: list):
    print(f"ls: called with args {args}")


def cmd_cd(args: list):
    print(f"cd: called with args {args}")


def cmd_exit(args: list):
    print("exit: Goodbye!")
    sys.exit(0)


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}


def execute_command(command: str, args: list):
    if command in COMMANDS:
        COMMANDS[command](args)
    else:
        print(f"Error: unknown command '{command}'. Type 'exit' to quit.", file=sys.stderr)

#Главный цикл REPL (Read-Eval-Print Loop).
def repl():
    print(f"VFS Emulator — Stage 1 (REPL)")
    print(f"Type 'exit' to quit.\n")

    while True:
        try:
            line = input(PROMPT)
        except EOFError, KeyboardInterrupt:
            # Обработка Ctrl+D
            print("\nexit: Goodbye!")
            sys.exit(0)
        except KeyboardInterrupt:
            # Обработка Ctrl+C
            print("\n(Interrupted. Type 'exit' to quit.)")
            continue

        command, args = parse_command(line)

        if command is None:
            continue

        execute_command(command, args)


if __name__ == "__main__":
    repl()
