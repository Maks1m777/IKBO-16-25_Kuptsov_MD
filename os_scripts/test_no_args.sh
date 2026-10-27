ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_no_args] запуск без параметров (stdin=/dev/null)"
python3 "$EMULATOR" < /dev/null
echo ">>> exit code: $?"