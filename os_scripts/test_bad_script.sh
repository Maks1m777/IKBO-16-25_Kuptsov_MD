ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_bad_script] --script vfs_scripts/DOES_NOT_EXIST.txt"
python3 "$EMULATOR" --script "$ROOT/vfs_scripts/DOES_NOT_EXIST.txt"
echo ">>> exit code: $? (ожидаем 1)"