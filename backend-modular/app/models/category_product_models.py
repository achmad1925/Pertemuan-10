from app.models.product_model import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # Relasi 1:N ke ProductItem
    products = db.relationship('ProductItem', backref='category', lazy=True)
    
    def to_dict(self):
        return {"id": self.id, "name": self.name}


class ProductItem(db.Model):
    __tablename__ = 'product_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category": self.category.name if self.category else None
        }