ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_vfs_only] --vfs vfs_data/deep.csv (stdin=/dev/null)"
python3 "$EMULATOR" --vfs "$ROOT/vfs_data/deep.csv" < /dev/null
echo ">>> exit code: $?"