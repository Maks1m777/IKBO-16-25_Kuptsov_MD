ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_both] --vfs + --script (with_errors.txt)"
python3 "$EMULATOR" \
    --vfs /data/vfs.img \
    --script "$ROOT/vfs_scripts/with_errors.txt"
echo ">>> exit code: $?"