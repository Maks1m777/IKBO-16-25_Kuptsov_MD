ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [vfs+deep, script mode] --vfs deep.csv --script vfs_demo.txt"
python3 "$EMULATOR" --vfs "$ROOT/vfs_data/deep.csv" \
    --script "$ROOT/vfs_scripts/vfs_demo.txt"
echo ">>> exit code: $?"; echo

echo ">>> [default, script mode] без --vfs --script vfs_demo.txt"
python3 "$EMULATOR" --script "$ROOT/vfs_scripts/vfs_demo.txt"
echo ">>> exit code: $?"; echo

echo ">>> [vfs+several, interactive mode] команды через pipe"
printf 'ls\nvfs-init\nexit\n' | python3 "$EMULATOR" --vfs "$ROOT/vfs_data/several_files.csv"
echo ">>> exit code: $?"