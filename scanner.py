import cv2
import numpy as np
from pyzbar.pyzbar import decode
import threading
import time


class BarcodeScanner:
    def __init__(self):
        self.camera = None
        self.scanning = False
        self.result = None

    def start_scan(self):
        """Запускает сканер и возвращает отсканированный штрихкод"""
        self.camera = cv2.VideoCapture(0)  # 0 - основная камера
        self.scanning = True
        self.result = None

        print("📸 Сканер запущен. Наведите на штрихкод. Нажмите ESC для выхода.")

        while self.scanning:
            ret, frame = self.camera.read()
            if not ret:
                break

            # Декодируем штрихкоды в кадре
            barcodes = decode(frame)

            for barcode in barcodes:
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = barcode.type

                # Рисуем прямоугольник вокруг штрихкода
                points = barcode.polygon
                if len(points) == 4:
                    pts = np.array([(p.x, p.y) for p in points], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)

                # Показываем текст со штрихкодом
                cv2.putText(frame, f"{barcode_data} ({barcode_type})",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Сохраняем результат и выходим
                self.result = barcode_data
                self.scanning = False
                print(f"✅ Найден штрихкод: {barcode_data}")
                break

            # Показываем кадр
            cv2.imshow('Сканер штрихкодов - нажмите ESC для выхода', frame)

            # Выход по ESC
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                self.scanning = False
                print("❌ Сканер остановлен")
                break

        self.stop()
        return self.result

    def stop(self):
        """Останавливает камеру и закрывает окна"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()


# Функция для быстрого сканирования
def scan_barcode():
    scanner = BarcodeScanner()
    return scanner.start_scan()


# Для тестирования
if __name__ == "__main__":
    print("Тест сканера штрихкодов")
    result = scan_barcode()
    if result:
        print(f"Результат: {result}")
    else:
        print("Ничего не найдено")