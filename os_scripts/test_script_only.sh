ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_script_only] --script vfs_scripts/basic.txt"
python3 "$EMULATOR" --script "$ROOT/vfs_scripts/basic.txt"
echo ">>> exit code: $?"