import uuid
from app import db
from sqlalchemy.dialects.mysql import BINARY

class Shop(db.Model):
    __tablename__ = 'shops'

    id = db.Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    owner_id = db.Column(BINARY(16), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    address = db.Column(db.String(255), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    shop_image_url = db.Column(db.String(255), nullable=True)
    is_open = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    owner = db.relationship('User', back_populates='shop')
    items = db.relationship('Item', back_populates='shop', cascade="all, delete-orphan")
    orders = db.relationship('Order', back_populates='shop', lazy=True)

    def get_uuid(self):
        return uuid.UUID(bytes=self.id)