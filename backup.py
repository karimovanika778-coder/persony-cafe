import os
import shutil
import sqlite3
from datetime import datetime
import zipfile
import json


class BackupManager:
    def __init__(self):
        self.backup_dir = 'backups'
        self.db_path = 'cafe_inventory.db'

        # Создаем папку для бэкапов, если её нет
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    def create_backup(self, comment=''):
        """Создаёт резервную копию базы данных"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(self.backup_dir, backup_name)

        # Создаём zip-архив с базой и метаданными
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Добавляем базу данных
            if os.path.exists(self.db_path):
                zipf.write(self.db_path, 'cafe_inventory.db')

            # Добавляем информацию о бэкапе
            info = {
                'created_at': timestamp,
                'comment': comment,
                'version': '1.0'
            }
            zipf.writestr('backup_info.json', json.dumps(info, indent=2, ensure_ascii=False))

        # Удаляем старые бэкапы (оставляем только 10 последних)
        self._cleanup_old_backups()

        return backup_path

    def restore_backup(self, backup_file):
        """Восстанавливает базу из резервной копии"""
        backup_path = os.path.join(self.backup_dir, backup_file)

        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Бэкап {backup_file} не найден")

        # Создаём временную папку для распаковки
        temp_dir = os.path.join(self.backup_dir, 'temp_restore')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        # Распаковываем архив
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(temp_dir)

        # Копируем базу на место
        db_backup = os.path.join(temp_dir, 'cafe_inventory.db')
        if os.path.exists(db_backup):
            # Делаем бэкап текущей базы перед восстановлением
            self.create_backup(comment='auto_before_restore')

            # Заменяем текущую базу
            shutil.copy2(db_backup, self.db_path)

            # Удаляем временную папку
            shutil.rmtree(temp_dir)
            return True

        shutil.rmtree(temp_dir)
        return False

    def list_backups(self):
        """Возвращает список всех бэкапов"""
        backups = []

        # Проверяем, существует ли папка
        if not os.path.exists(self.backup_dir):
            return backups

        for f in os.listdir(self.backup_dir):
            if f.startswith('backup_') and f.endswith('.zip'):
                path = os.path.join(self.backup_dir, f)
                size = os.path.getsize(path)
                created = f.replace('backup_', '').replace('.zip', '')

                # Пытаемся прочитать комментарий из архива
                comment = ''
                try:
                    with zipfile.ZipFile(path, 'r') as zipf:
                        if 'backup_info.json' in zipf.namelist():
                            info = json.loads(zipf.read('backup_info.json'))
                            comment = info.get('comment', '')
                except:
                    pass

                backups.append({
                    'filename': f,
                    'created': created,
                    'size': self._format_size(size),
                    'comment': comment
                })

        # Сортируем по дате (новые сверху)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    def _cleanup_old_backups(self, keep=10):
        """Оставляет только последние keep бэкапов"""
        backups = self.list_backups()
        if len(backups) > keep:
            for backup in backups[keep:]:
                try:
                    os.remove(os.path.join(self.backup_dir, backup['filename']))
                except:
                    pass

    def _format_size(self, size):
        """Форматирует размер файла"""
        for unit in ['Б', 'КБ', 'МБ']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} ГБ"


# Функция для автоматического бэкапа при запуске
def auto_backup():
    try:
        manager = BackupManager()
        backup_path = manager.create_backup(comment='auto_backup')
        print(f"✅ Автоматический бэкап создан: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"❌ Ошибка авто-бэкапа: {e}")
        return None


if __name__ == '__main__':
    # Тестирование
    manager = BackupManager()
    print("📦 Создание бэкапа...")
    path = manager.create_backup(comment='тестовый бэкап')
    print(f"✅ Бэкап создан: {path}")

    print("\n📋 Список бэкапов:")
    for b in manager.list_backups():
        print(f"  • {b['filename']} - {b['size']} - {b['comment']}")