# Тестовый скрипт для демонстрации работы Этапа 1 (REPL)
# Запускать из директории tests/: ./test_stage1.sh
# Или из корня репозитория: bash tests/test_stage1.sh

# Переходим в директорию скрипта, чтобы относительные пути работали корректно
cd "$(dirname "$0")" || exit 1

echo "=== Тест 1: Команда ls без аргументов ==="
echo "ls" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 2: Команда ls с аргументами ==="
echo "ls -la /home/user" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 3: Команда cd с аргументом ==="
echo "cd /tmp" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 4: Команда cd без аргументов ==="
echo "cd" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 5: Неизвестная команда (обработка ошибки) ==="
echo "rm -rf /" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 6: Пустой ввод перед командой ==="
printf "\nls\n" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 7: Команда exit ==="
echo "exit" | python3 ../vfs_emulator.py

echo ""
echo "=== Тест 8: Несколько команд подряд (сценарий диалога) ==="
printf "ls\ncd /home\nls -la\nexit\n" | python3 ../vfs_emulator.py

echo ""
echo "=== Все тесты завершены ==="