import uuid
from app import db
from sqlalchemy.dialects.mysql import BINARY

class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    shop_id = db.Column(BINARY(16), db.ForeignKey('shops.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationship
    shop = db.relationship('Shop', back_populates='items')

    def get_uuid(self):
        return uuid.UUID(bytes=self.id)