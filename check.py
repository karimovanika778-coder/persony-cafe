import os

print("=" * 50)
print("ПРОВЕРКА ФАЙЛОВ")
print("=" * 50)

# Текущая папка
current_dir = os.getcwd()
print(f"Текущая папка: {current_dir}")

# Проверяем папку templates
templates_path = os.path.join(current_dir, 'templates')
print(f"\nПапка templates: {templates_path}")
print(f"Существует: {os.path.exists(templates_path)}")

if os.path.exists(templates_path):
    # Смотрим все файлы в templates
    files = os.listdir(templates_path)
    print(f"\nВсе файлы в templates ({len(files)}):")
    for f in files:
        print(f"  - {f}")

    # Ищем scan.html
    if 'scan.html' in files:
        print("\n✅ scan.html НАЙДЕН!")
    else:
        print("\n❌ scan.html НЕ НАЙДЕН!")

        # Ищем похожие файлы
        scan_files = [f for f in files if 'scan' in f.lower()]
        if scan_files:
            print(f"Похожие файлы: {scan_files}")
else:
    print("\n❌ Папка templates не найдена!")

print("\n" + "=" * 50)