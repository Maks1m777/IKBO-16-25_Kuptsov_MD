ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

for csv in minimal.csv several_files.csv deep.csv; do
    echo ">>> [test_vfs_load] --vfs vfs_data/$csv"
    python3 "$EMULATOR" --vfs "$ROOT/vfs_data/$csv" < /dev/null
    echo ">>> exit code: $?"
    echo
done