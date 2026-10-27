ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for s in test_vfs_load.sh test_vfs_commands.sh test_vfs_errors.sh; do
    echo "################ $s ################"
    bash "$ROOT/os_scripts/$s"
    echo
done