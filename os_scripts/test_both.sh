ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_both] --vfs several_files.csv + --script basic.txt"
python3 "$EMULATOR" \
    --vfs "$ROOT/vfs_data/several_files.csv" \
    --script "$ROOT/vfs_scripts/basic.txt"
echo ">>> exit code: $?"