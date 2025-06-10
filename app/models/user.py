import uuid
from app import db, bcrypt
from sqlalchemy.dialects.mysql import BINARY

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(BINARY(16), primary_key=True, default=lambda: uuid.uuid4().bytes)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), unique=False, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('customer', 'owner', 'rider'), nullable=False)
    current_lat = db.Column(db.Numeric(10, 8), nullable=True)
    current_lng = db.Column(db.Numeric(11, 8), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    shop = db.relationship('Shop', back_populates='owner', uselist=False, cascade="all, delete-orphan")
    orders_placed = db.relationship('Order', foreign_keys='Order.customer_id', back_populates='customer', lazy=True)
    orders_handled = db.relationship('Order', foreign_keys='Order.rider_id', back_populates='rider', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def get_uuid(self):
        return uuid.UUID(bytes=self.id)