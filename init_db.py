from app import app, db
from database import Workshop, Product, Stock

with app.app_context():
    # Создаем таблицы
    db.create_all()

    # Очищаем старые данные
    Workshop.query.delete()
    Product.query.delete()
    Stock.query.delete()

    # Создаем цеха
    workshops = [
        Workshop(name='Горячий цех', description='Горячие блюда, супы, гарниры'),
        Workshop(name='Холодный цех', description='Салаты, закуски, холодные напитки'),
        Workshop(name='Мясной цех', description='Разделка мяса, полуфабрикаты'),
        Workshop(name='Кондитерский цех', description='Десерты, выпечка'),
        Workshop(name='Открытая кухня', description='Блюда на виду у гостей'),
        Workshop(name='Заморозка', description='Замороженные продукты')
    ]

    db.session.add_all(workshops)

    # Создаем тестовые продукты
    products = [
        Product(name='Вырезка говяжья', unit='кг', category='Мясо', type='ingredient'),
        Product(name='Куриное филе', unit='кг', category='Птица', type='ingredient'),
        Product(name='Лосось слабосоленый', unit='кг', category='Рыба', type='retail'),
        Product(name='Чизкейк', unit='шт', category='Десерты', type='ready_dish'),
        Product(name='Сливочное масло', unit='кг', category='Молочка', type='ingredient'),
    ]

    db.session.add_all(products)
    db.session.commit()

    print("✅ Цеха и продукты успешно добавлены!")

    # Добавляем остатки
    stock1 = Stock(product_id=1, workshop_id=3, quantity=5.5)  # говядина в мясном
    stock2 = Stock(product_id=2, workshop_id=3, quantity=3.0)  # курица в мясном
    stock3 = Stock(product_id=3, workshop_id=2, quantity=2.0)  # лосось в холодном
    stock4 = Stock(product_id=4, workshop_id=4, quantity=4.0)  # чизкейк в кондитерском
    stock5 = Stock(product_id=5, workshop_id=5, quantity=1.2)  # масло на открытой кухне

    db.session.add_all([stock1, stock2, stock3, stock4, stock5])
    db.session.commit()

    print("✅ Остатки добавлены!")

    # Проверяем
    print(f"Всего цехов: {Workshop.query.count()}")
    print(f"Всего продуктов: {Product.query.count()}")
    print(f"Всего записей об остатках: {Stock.query.count()}")

    # Пример добавления продуктов с разными типами
    products = [
        Product(name='Вырезка говяжья', unit='кг', category='Мясо', type='ingredient'),
        Product(name='Куриное филе', unit='кг', category='Птица', type='ingredient'),
        Product(name='Соль поваренная', unit='кг', category='Специи', type='ingredient'),
        Product(name='Котлеты замороженные', unit='шт', category='Полуфабрикаты', type='semi_finished'),
        Product(name='Тесто слоеное', unit='кг', category='Полуфабрикаты', type='semi_finished'),
        Product(name='Чизкейк готовый', unit='шт', category='Десерты', type='ready_dish'),
        Product(name='Салат Цезарь', unit='порц', category='Салаты', type='ready_dish'),
        Product(name='Лосось слабосоленый (привозной)', unit='кг', category='Рыба', type='retail'),
        Product(name='Сок апельсиновый', unit='шт', category='Напитки', type='retail'),
    ]