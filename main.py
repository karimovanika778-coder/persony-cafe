from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db, Workshop, Product, Stock, Movement, Order, Recipe, RecipeIngredient
from datetime import datetime
import os

# Все проблемные библиотеки пока закомментированы
# import cv2
# import numpy as np
# from pyzbar.pyzbar import decode

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafe_inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Создаем таблицы при первом запуске
with app.app_context():
    db.create_all()
    print("✅ База данных создана")

# Главная страница - выбор цеха
@app.route('/')
def index():
    workshops = Workshop.query.all()
    return render_template('index.html', workshops=workshops)

# Временная заглушка для сканера
@app.route('/scan')
def scan():
    return render_template('scan.html')

# Простой маршрут для проверки
@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

# Остальные маршруты пока можно оставить как есть
# (они будут работать, если не используют cv2)

# ... (остальной код оставьте без изменений)

if __name__ == '__main__':
    app.run(debug=True)
