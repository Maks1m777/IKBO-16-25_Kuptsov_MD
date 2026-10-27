import argparse
import os
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


def build_arg_parser():
    parser = argparse.ArgumentParser(
        prog="vfs_emulator",
        description="VFS Emulator — эмулятор оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "-v", "--vfs",
        dest="vfs_path",
        default=None,
        metavar="PATH",
        help="Путь к физическому расположению VFS.",
    )
    parser.add_argument(
        "-s", "--script",
        dest="script_path",
        default=None,
        metavar="PATH",
        help="Путь к стартовому скрипту команд эмулятора.",
    )
    return parser


def debug_print_config(cfg: dict):
    vfs = cfg["vfs_path"] if cfg["vfs_path"] else "<not set>"
    script = cfg["script_path"] if cfg["script_path"] else "<not set>"
    mode = "script" if cfg["script_path"] else "interactive"
    print(f"[config] vfs_path    = {vfs}", file=sys.stderr)
    print(f"[config] script_path = {script}", file=sys.stderr)
    print(f"[config] mode        = {mode}", file=sys.stderr)



#Скриптовый режим
def run_script(path: str):
    if not os.path.isfile(path):
        print(f"Error: startup script not found: {path}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.rstrip("\n")
                if not line.strip():
                    continue
                # Имитация ввода
                print(f"{PROMPT}{line}")
                command, args = parse_command(line)
                if command is None:
                    continue
                execute_command(command, args)
    except KeyboardInterrupt:
        # В скриптовом режиме Ctrl+C прерывает выполнение скрипта.
        print("\n[script] interrupted", file=sys.stderr)
        sys.exit(130)


#Интерактивный REPL (Read-Eval-Print Loop)
def repl():
    print(f"VFS Emulator — interactive mode")
    print(f"Type 'exit' to quit.\n")

    while True:
        try:
            line = input(PROMPT)
        except EOFError:
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


def main():
    args = build_arg_parser().parse_args()
    cfg = {"vfs_path": args.vfs_path, "script_path": args.script_path}

    # Отладочный вывод всех заданных параметров при запуске.
    debug_print_config(cfg)

    if cfg["script_path"]:
        run_script(cfg["script_path"])
    else:
        repl()


if __name__ == "__main__":
    main()
