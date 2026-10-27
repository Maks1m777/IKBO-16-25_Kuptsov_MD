ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"

echo ">>> [test_vfs_only] --vfs /data/vfs.img (stdin=/dev/null)"
python3 "$EMULATOR" --vfs /data/vfs.img < /dev/null
echo ">>> exit code: $?"