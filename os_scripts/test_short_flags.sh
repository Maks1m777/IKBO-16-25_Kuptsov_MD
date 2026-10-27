ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_short_flags] -v minimal.csv + -s exit_mid.txt"
python3 "$EMULATOR" \
    -v "$ROOT/vfs_data/minimal.csv" \
    -s "$ROOT/vfs_scripts/exit_mid.txt"
echo ">>> exit code: $?"