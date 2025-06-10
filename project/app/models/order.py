import uuid
from app import db
from sqlalchemy.dialects.mysql import BINARY

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    customer_id = db.Column(BINARY(16), db.ForeignKey('users.id'), nullable=False)
    shop_id = db.Column(BINARY(16), db.ForeignKey('shops.id'), nullable=False)
    rider_id = db.Column(BINARY(16), db.ForeignKey('users.id'), nullable=True)
    order_status = db.Column(db.Enum('pending', 'confirmed', 'preparing', 'ready_for_pickup', 'picked_up', 'delivered', 'cancelled'), nullable=False, default='pending')
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    customer = db.relationship('User', foreign_keys=[customer_id], back_populates='orders_placed')
    rider = db.relationship('User', foreign_keys=[rider_id], back_populates='orders_handled')
    shop = db.relationship('Shop', back_populates='orders')
    order_items = db.relationship('OrderItem', back_populates='order', cascade="all, delete-orphan")

    def get_uuid(self):
        return uuid.UUID(bytes=self.id)

class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    order_id = db.Column(BINARY(16), db.ForeignKey('orders.id'), nullable=False)
    item_id = db.Column(BINARY(16), db.ForeignKey('items.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    order = db.relationship('Order', back_populates='order_items')
    item = db.relationship('Item')

    def get_uuid(self):
        return uuid.UUID(bytes=self.id)