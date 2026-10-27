ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [missing csv] ожидаем exit 1"
python3 "$EMULATOR" --vfs "$ROOT/vfs_data/NOPE.csv" < /dev/null
echo ">>> exit code: $?"; echo

echo ">>> [broken header] ожидаем exit 1"
python3 "$EMULATOR" --vfs "$ROOT/vfs_data/broken_header.csv" < /dev/null
echo ">>> exit code: $?"; echo

echo ">>> [broken rows] ожидаем exit 0 + warnings в stderr"
python3 "$EMULATOR" --vfs "$ROOT/vfs_data/broken_rows.csv" \
    --script "$ROOT/vfs_scripts/vfs_demo.txt"
echo ">>> exit code: $?"