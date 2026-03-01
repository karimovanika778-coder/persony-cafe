from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Модель цеха
class Workshop(db.Model):
    __tablename__ = 'workshops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # горячий, холодный и т.д.
    description = db.Column(db.String(200))

    # Связи
    products = db.relationship('Product', secondary='stock', viewonly=True)
    stocks = db.relationship('Stock', back_populates='workshop', lazy=True)
    movements = db.relationship('Movement', back_populates='workshop', lazy=True)
    orders = db.relationship('Order', back_populates='workshop', lazy=True)
    recipes = db.relationship('Recipe', back_populates='workshop', lazy=True)

    def __repr__(self):
        return f'<Workshop {self.name}>'


# Модель продукта
class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)  # название продукта
    barcode = db.Column(db.String(50), unique=True)  # штрихкод
    unit = db.Column(db.String(10), nullable=False)  # кг, шт, л
    category = db.Column(db.String(50))  # мясо, овощи и т.д.
    type = db.Column(db.String(20), default='ingredient')  # ingredient, ready_dish, retail, semi_finished

    # Связи
    stocks = db.relationship('Stock', back_populates='product', lazy=True)
    movements = db.relationship('Movement', back_populates='product', lazy=True)
    orders = db.relationship('Order', back_populates='product', lazy=True)
    recipes_as_dish = db.relationship('Recipe', foreign_keys='Recipe.dish_id', back_populates='dish', lazy=True)
    used_in_recipes = db.relationship('RecipeIngredient', back_populates='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'


# Модель остатков (связь продукта с цехом)
class Stock(db.Model):
    __tablename__ = 'stock'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    quantity = db.Column(db.Float, default=0.0)  # текущее количество
    min_stock = db.Column(db.Float, default=0.0)  # минимальный остаток
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    product = db.relationship('Product', back_populates='stocks')
    workshop = db.relationship('Workshop', back_populates='stocks')

    # Уникальность: один продукт в одном цехе - одна запись
    __table_args__ = (db.UniqueConstraint('product_id', 'workshop_id'),)

    def __repr__(self):
        return f'<Stock {self.product.name} в {self.workshop.name}: {self.quantity}>'


# Модель движений (приход/расход)
class Movement(db.Model):
    __tablename__ = 'movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # положительное - приход, отрицательное - расход
    movement_type = db.Column(db.String(20))  # 'income' (приход) или 'expense' (расход)
    reason = db.Column(db.String(200))  # причина: поставка, списание, возврат и т.д.
    comment = db.Column(db.String(500))  # комментарий
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(100), default='повар')

    # Связи
    product = db.relationship('Product', back_populates='movements')
    workshop = db.relationship('Workshop', back_populates='movements')

    def __repr__(self):
        return f'<Movement {self.movement_type}: {self.product.name} {self.quantity}>'


# Модель заказов
class Order(db.Model):
    __tablename__ = 'orders'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10))
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'cancelled'
    priority = db.Column(db.String(20), default='normal')  # 'high', 'normal', 'low'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    comment = db.Column(db.String(500))
    created_by = db.Column(db.String(100), default='шеф')

    # Связи
    product = db.relationship('Product', back_populates='orders')
    workshop = db.relationship('Workshop', back_populates='orders')

    def __repr__(self):
        return f'<Order {self.product.name}: {self.quantity} {self.unit}>'


# Модель рецепта (технологической карты)
class Recipe(db.Model):
    __tablename__ = 'recipes'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # готовое блюдо
    name = db.Column(db.String(200), nullable=False)  # название рецепта
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'), nullable=False)  # где готовят
    portions = db.Column(db.Integer, default=1)  # выход в порциях
    cooking_time = db.Column(db.Integer)  # время приготовления в минутах
    instructions = db.Column(db.Text)  # инструкция по приготовлению
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    dish = db.relationship('Product', foreign_keys=[dish_id], back_populates='recipes_as_dish')
    workshop = db.relationship('Workshop', back_populates='recipes')
    ingredients = db.relationship('RecipeIngredient', back_populates='recipe', cascade='all, delete-orphan')

    def total_cost(self):
        """Расчёт общей себестоимости блюда"""
        return sum(ing.cost() for ing in self.ingredients)

    def __repr__(self):
        return f'<Recipe {self.name}>'


# Модель ингредиента в рецепте
class RecipeIngredient(db.Model):
    __tablename__ = 'recipe_ingredients'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # количество на одну порцию
    unit = db.Column(db.String(10))  # единица измерения (может отличаться от базовой)
    notes = db.Column(db.String(200))  # примечания (например, "очищенный", "без костей")

    # Связи
    recipe = db.relationship('Recipe', back_populates='ingredients')
    product = db.relationship('Product', back_populates='used_in_recipes')

    def cost(self):
        """Стоимость ингредиента в рецепте"""
        # Для простоты пока возвращаем 0
        # В реальности нужно брать среднюю цену из приходов
        return 0

    def __repr__(self):
        return f'<Ingredient {self.product.name}: {self.quantity}>'