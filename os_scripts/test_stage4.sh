ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [stage4 default VFS] --script stage4_commands.txt (все режимы + ошибки)"
python3 "$EMULATOR" --script "$ROOT/vfs_scripts/stage4_commands.txt"
echo ">>> exit code: $?"; echo

echo ">>> [stage4 loaded VFS deep.csv] команды поверх загруженного дерева (pipe)"
printf 'pwd\ncd /home/alice/projects\nls -l\ncat notes.txt\ncat src/main.c\nls /etc/hosts\npwd\nexit\n' \
    | python3 "$EMULATOR" --vfs "$ROOT/vfs_data/deep.csv"
echo ">>> exit code: $?"