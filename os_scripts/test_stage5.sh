ROOT="$(cd "$(dirname "$0")/.." && pwd)"
EMULATOR="$ROOT/vfs_emulator.py"
DEEP="$ROOT/vfs_data/deep.csv"

hash_file() {
    python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$1"
}

echo ">>> [A] stage5_commands.txt на default VFS (все режимы + ошибки + vfs-init)"
python3 "$EMULATOR" --script "$ROOT/vfs_scripts/stage5_commands.txt"
echo ">>> exit code: $?"; echo

echo ">>> [B1] мутации поверх загруженной deep.csv (видимы в том же процессе)"
BEFORE="$(hash_file "$DEEP")"
printf 'cd /home/alice/projects\ncat notes.txt\nmkdir -p /mnt/test\ntouch /mnt/test/new.txt\nls -l /mnt/test\nls /mnt\nexit\n' \
    | python3 "$EMULATOR" --vfs "$DEEP"
echo ">>> exit code: $?"; echo

AFTER="$(hash_file "$DEEP")"
echo ">>> CSV sha256 before = $BEFORE"
echo ">>> CSV sha256 after  = $AFTER"
if [ "$BEFORE" = "$AFTER" ]; then
    echo ">>> OK: deep.csv НЕ изменён -> мутации только в памяти"
else
    echo ">>> FAIL: deep.csv изменился на диске!"
fi
echo

echo ">>> [B2] отдельный прогон: мутации из B1 НЕ персистентны (ожидаем ошибку)"
printf 'ls /mnt\nexit\n' | python3 "$EMULATOR" --vfs "$DEEP"
echo ">>> exit code: $?"