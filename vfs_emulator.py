import argparse
import base64
import binascii
import csv
import os
import sys
import shlex

VFS_NAME = "VFS"
PROMPT = f"{VFS_NAME}$ "

class VFSNode:
    __slots__ = ("name", "is_dir", "children", "data")

    def __init__(self, name: str, is_dir: bool):
        self.name = name
        self.is_dir = is_dir
        self.children = {}
        self.data = b""

class VFS:
    def __init__(self):
        self.root = VFSNode("", True)
        self._index = {"/": self.root}

class EmulatorState:
    def __init__(self):
        self.vfs = None
        self.vfs_source = None
        self.cwd = "/"

STATE = EmulatorState()


def _resolve_path(path: str, base: str = "/"):
    if not path:
        path = base
    if path.startswith("/"):
        parts = path.split("/")
    else:
        parts = (base.rstrip("/") + "/" + path).split("/")

    out = []
    for p in parts:
        if p == "" or p == ".":
            continue
        if p == "..":
            if out:
                out.pop()
            continue
        out.append(p)
    return "/" + "/".join(out)

def _add_node(vfs: VFS, ntype: str, raw_path: str, data: bytes, warn):
    norm = _resolve_path(raw_path, "/")
    comps = norm.split("/")[1:]
    if not comps:
        if ntype != "dir":
            warn(f"cannot create file at root '/', skipped")
        return
    node = vfs.root
    cur_path = ""
    for i, c in enumerate(comps):
        cur_path = cur_path + "/" + c
        last = (i == len(comps) - 1)
        child = node.children.get(c)
        if last:
            if child is not None:
                warn(f"duplicate node '{norm}', skipped")
                return
            new = VFSNode(c, ntype == "dir")
            if ntype == "file":
                new.data = data
            node.children[c] = new
            vfs._index[cur_path] = new
            return
        if child is None:
            d = VFSNode(c, True)
            node.children[c] = d
            vfs._index[cur_path] = d
            node = d
        elif not child.is_dir:
            warn(f"cannot descend into file at '{cur_path}', skipped '{norm}'")
            return
        else:
            node = child

def default_vfs():
    vfs = VFS()
    noop = lambda _m: None
    spec = [
        ("dir",  "/",                      ""),
        ("dir",  "/home",                  ""),
        ("dir",  "/home/user",             ""),
        ("file", "/home/user/welcome.txt", "aGVsbG8="),   # "hello"
        ("dir",  "/etc",                   ""),
        ("file", "/etc/motd",              "d29ybGQ="),   # "world"
        ("dir",  "/tmp",                   ""),
    ]
    for ntype, p, b64 in spec:
        data = base64.b64decode(b64) if (ntype == "file" and b64) else b""
        _add_node(vfs, ntype, p, data, noop)
    return vfs

def load_vfs_from_csv(path: str):
    vfs = VFS()

    def warn(msg: str):
        print(f"[vfs-load] warning: {msg}", file=sys.stderr)

    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            fields = reader.fieldnames or []
            if "type" not in fields or "path" not in fields:
                raise ValueError("CSV header must contain at least 'type' and 'path' columns")
            for lineno, row in enumerate(reader, start=2):
                ntype = (row.get("type") or "").strip().lower()
                raw_path = (row.get("path") or "")
                content = (row.get("content") or "")
                if ntype not in ("dir", "file"):
                    warn(f"line {lineno}: unknown type '{ntype}', skipped")
                    continue
                if not raw_path.strip():
                    warn(f"line {lineno}: empty path, skipped")
                    continue
                data = b""
                if ntype == "file":
                    content = content.strip()
                    if content:
                        try:
                            data = base64.b64decode(content, validate=True)
                        except (binascii.Error, ValueError):
                            warn(f"line {lineno}: invalid base64 content, skipped")
                            continue
                _add_node(vfs, ntype, raw_path, data, warn)
    except (OSError, csv.Error, ValueError) as exc:
        print(f"Error: failed to load VFS from '{path}': {exc}", file=sys.stderr)
        sys.exit(1)
    return vfs

def vfs_stats(vfs: VFS):
    dirs = files = 0

    def walk(node: VFSNode):
        nonlocal dirs, files
        if node.is_dir:
            dirs += 1
            for ch in node.children.values():
                walk(ch)
        else:
            files += 1

    walk(vfs.root)
    return dirs, files

def vfs_to_lines(vfs: VFS):
    lines = []

    def walk(node: VFSNode, prefix: str):
        if node is vfs.root:
            lines.append("/ [dir]")
        else:
            kind = "dir" if node.is_dir else "file"
            size = "" if node.is_dir else f" ({len(node.data)} bytes)"
            lines.append(f"{prefix}{node.name} [{kind}]{size}")
        if node.is_dir:
            kids = sorted(node.children.values(), key=lambda n: (not n.is_dir, n.name))
            for ch in kids:
                walk(ch, prefix + "  ")
    walk(vfs.root, "")
    return lines

def parse_command(line: str):
    line = line.strip()
    if not line:
        return None, []
    parts = shlex.split(line)
    command = parts[0]
    args = parts[1:]
    return command, args

def _abs(path: str):
    return _resolve_path(path, STATE.cwd)

def _lookup(abspath: str):
    return STATE.vfs._index.get(abspath)

def _write_bytes(data: bytes):
    sys.stdout.flush()
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()

def _parse_ls_flags(args: list):
    show_all = False
    long_fmt = False
    paths = []
    seen_dd = False
    for tok in args:
        if seen_dd:
            paths.append(tok)
            continue
        if tok == "--":
            seen_dd = True
            continue
        if len(tok) > 1 and tok[0] == "-" and tok[1] == "-":
            return (False, False, [], f"ls: unrecognized option '{tok}'")
        if len(tok) > 1 and tok[0] == "-":
            for ch in tok[1:]:
                if ch == "a":
                    show_all = True
                elif ch == "l":
                    long_fmt = True
                else:
                    return (False, False, [], f"ls: invalid option -- '{ch}'")
            continue
        if tok == "-":
            return (False, False, [], "ls: invalid option -- '-'")
        paths.append(tok)
    return (show_all, long_fmt, paths, None)

def _ls_long_line(node: VFSNode):
    if node.is_dir:
        perms = "drwxr-xr-x"
        size = 4096
    else:
        perms = "-rw-r--r--"
        size = len(node.data)
    return f"{perms} 1 vfs vfs {size:>8} {node.name}"

def cmd_ls(args: list):
    show_all, long_fmt, paths, err = _parse_ls_flags(args)
    if err:
        print(err, file=sys.stderr)
        return
    if not paths:
        paths = [STATE.cwd]
    multi = len(paths) > 1
    first = True
    for p in paths:
        ap = _abs(p)
        node = _lookup(ap)
        if node is None:
            print(f"ls: cannot access '{p}': No such file or directory", file=sys.stderr)
            continue
        if multi:
            if not first:
                print()
            print(f"{p}:")
        first = False
        if node.is_dir:
            entries = sorted(node.children.keys())
            if not show_all:
                entries = [e for e in entries if not e.startswith(".")]
            if long_fmt:
                for name in entries:
                    print(_ls_long_line(node.children[name]))
            else:
                for name in entries:
                    print(name)
        else:
            print(_ls_long_line(node) if long_fmt else p)

def cmd_cd(args: list):
    if len(args) > 1:
        print("cd: too many arguments", file=sys.stderr)
        return
    target = "/" if not args else _abs(args[0])
    node = _lookup(target)
    if node is None:
        print(f"cd: {args[0]}: No such file or directory", file=sys.stderr)
        return
    if not node.is_dir:
        print(f"cd: {args[0]}: Not a directory", file=sys.stderr)
        return
    STATE.cwd = target

def cmd_cat(args: list):
    if not args:
        print("cat: missing operand; reading from stdin is not supported here",
              file=sys.stderr)
        return
    for p in args:
        ap = _abs(p)
        node = _lookup(ap)
        if node is None:
            print(f"cat: {p}: No such file or directory", file=sys.stderr)
            continue
        if node.is_dir:
            print(f"cat: {p}: Is a directory", file=sys.stderr)
            continue
        _write_bytes(node.data)

def cmd_pwd(args: list):
    print(STATE.cwd)

def cmd_exit(args: list):
    print("exit: Goodbye!")
    sys.exit(0)

def cmd_vfs_init(args: list):
    STATE.vfs = default_vfs()
    STATE.vfs_source = None
    STATE.cwd = "/"
    print("vfs-init: current VFS replaced with default (in-memory); "
          "physical representation cleared.")
    if args:
        print(f"vfs-init: ignoring unexpected arguments {args}", file=sys.stderr)
    for ln in vfs_to_lines(STATE.vfs):
        print(ln)

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "cat": cmd_cat,
    "pwd": cmd_pwd,
    "exit": cmd_exit,
    "vfs-init": cmd_vfs_init
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

def debug_print_vfs(state: EmulatorState):
    src = state.vfs_source if state.vfs_source else "<default in-memory>"
    dirs, files = vfs_stats(state.vfs)
    print(f"[vfs] source = {src}", file=sys.stderr)
    print(f"[vfs] nodes  : dirs={dirs} files={files}", file=sys.stderr)
    print("[vfs] structure:", file=sys.stderr)
    for ln in vfs_to_lines(state.vfs):
        print(ln, file=sys.stderr)

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

    debug_print_config(cfg)

    if cfg["vfs_path"]:
        if not os.path.isfile(cfg["vfs_path"]):
            print(f"Error: VFS file not found: {cfg['vfs_path']}", file=sys.stderr)
            sys.exit(1)
        STATE.vfs = load_vfs_from_csv(cfg["vfs_path"])
        STATE.vfs_source = cfg["vfs_path"]
    else:
        STATE.vfs = default_vfs()
        STATE.vfs_source = None

    debug_print_vfs(STATE)

    if cfg["script_path"]:
        run_script(cfg["script_path"])
    else:
        repl()

if __name__ == "__main__":
    main()
