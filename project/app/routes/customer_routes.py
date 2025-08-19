from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from app import db
from ..models.user import User
from ..models.shop import Shop
from ..models.item import Item
from ..models.order import Order, OrderItem
from .utils import login_required, role_required
import uuid
from math import radians, sin, cos, sqrt, atan2

customer_bp = Blueprint('customer_bp', __name__)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Radius of Earth in kilometers.
    R = 6371.0 

    # Convert decimal degrees to radians
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Difference in coordinates
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    
    distance = R * c
    return distance

@customer_bp.route('/dashboard')
@login_required
@role_required('customer')
def dashboard():
    shops = Shop.query.filter_by(is_open=True).all()
    return render_template('customer/dashboard.html', shops=shops)

@customer_bp.route('/shop/<shop_uuid>')
@login_required
@role_required('customer')
def view_shop(shop_uuid):
    shop_id_bytes = uuid.UUID(shop_uuid).bytes
    shop = Shop.query.get(shop_id_bytes)
    if not shop:
        flash('Shop not found.', 'danger')
        return redirect(url_for('customer_bp.dashboard'))
    
    items = Item.query.filter_by(shop_id=shop_id_bytes, is_available=True).all()
    return render_template('customer/shop_detail.html', shop=shop, items=items)

@customer_bp.route('/cart/add/<item_uuid>', methods=['POST'])
@login_required
@role_required('customer')
def add_to_cart(item_uuid):
    cart = session.get('cart', {})
    quantity = int(request.form.get('quantity', 1))

    cart[item_uuid] = cart.get(item_uuid, 0) + quantity
    
    session['cart'] = cart
    flash('Item added to cart.', 'success')
    
    item_id_bytes = uuid.UUID(item_uuid).bytes
    item = Item.query.get(item_id_bytes)
    return redirect(url_for('customer_bp.view_shop', shop_uuid=str(item.shop.get_uuid())))

@customer_bp.route('/cart')
@login_required
@role_required('customer')
def view_cart():
    cart = session.get('cart', {})
    if not cart:
        return render_template('customer/cart.html', cart_items=[], total_price=0)

    cart_items = []
    total_price = 0
    
    for item_uuid_str, quantity in cart.items():
        item_id_bytes = uuid.UUID(item_uuid_str).bytes
        item = Item.query.get(item_id_bytes)
        if item:
            subtotal = item.price * quantity
            cart_items.append({
                'uuid': item_uuid_str,
                'name': item.name,
                'price': item.price,
                'quantity': quantity,
                'subtotal': subtotal
            })
            total_price += subtotal
            
    return render_template('customer/cart.html', cart_items=cart_items, total_price=total_price)

@customer_bp.route('/cart/update/<item_uuid>', methods=['POST'])
@login_required
@role_required('customer')
def update_cart(item_uuid):
    cart = session.get('cart', {})
    new_quantity = int(request.form.get('quantity'))

    if new_quantity > 0:
        cart[item_uuid] = new_quantity
    elif new_quantity == 0:
        if item_uuid in cart:
            del cart[item_uuid]

    session['cart'] = cart
    return redirect(url_for('customer_bp.view_cart'))


@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
@role_required('customer')
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('customer_bp.dashboard'))
    
    cart_items_data = []
    total_price = 0
    shop_id = None

    for item_uuid_str, quantity in cart.items():
        item_id_bytes = uuid.UUID(item_uuid_str).bytes
        item = Item.query.get(item_id_bytes)
        if item:
            if shop_id is None:
                shop_id = item.shop_id
            elif shop_id != item.shop_id:
                flash('You can only order from one shop at a time. Please clear your cart to start a new order.', 'danger')
                return redirect(url_for('customer_bp.view_cart'))
            
            cart_items_data.append({'item': item, 'quantity': quantity})
            total_price += item.price * quantity

    if request.method == 'POST':
        delivery_address = request.form.get('delivery_address')
        if not delivery_address:
            flash('Delivery address is required.', 'danger')
            return render_template('customer/checkout.html', cart_items=cart_items_data, total_price=total_price)
            
        customer_id_bytes = uuid.UUID(session['user_id']).bytes

        new_order = Order(
            id=uuid.uuid4().bytes,
            customer_id=customer_id_bytes,
            shop_id=shop_id,
            total_price=total_price,
            delivery_address=delivery_address
        )
        db.session.add(new_order)
        
        for data in cart_items_data:
            item = data['item']
            quantity = data['quantity']
            order_item = OrderItem(
                id=uuid.uuid4().bytes,
                order_id=new_order.id,
                item_id=item.id,
                quantity=quantity,
                price_at_purchase=item.price
            )
            db.session.add(order_item)
            
        db.session.commit()
        
        session.pop('cart', None)
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('customer_bp.view_orders'))

    return render_template('customer/checkout.html', cart_items=cart_items_data, total_price=total_price)

@customer_bp.route('/orders')
@login_required
@role_required('customer')
def view_orders():
    customer_id_bytes = uuid.UUID(session['user_id']).bytes
    orders = Order.query.filter_by(customer_id=customer_id_bytes).order_by(Order.created_at.desc()).all()
    return render_template('customer/orders.html', orders=orders)



@customer_bp.route('/order/track/<order_uuid>')
@login_required
@role_required('customer')
def track_order(order_uuid):
    order_id_bytes = uuid.UUID(order_uuid).bytes
    order = Order.query.get(order_id_bytes)
    
    customer_id_str = session.get('user_id')
    if not order or str(order.customer.get_uuid()) != customer_id_str:
        flash("Order not found.", 'danger')
        return redirect(url_for('customer_bp.view_orders'))

    if order.order_status != 'picked_up' or not order.rider.current_lat or not order.customer.current_lat:
        return render_template('customer/track_order_unavailable.html', order=order)

    rider_coords = (order.rider.current_lat, order.rider.current_lng)
    customer_coords = (order.customer.current_lat, order.customer.current_lng)

    distance_km = haversine_distance(rider_coords[0], rider_coords[1], customer_coords[0], customer_coords[1])
    
    avg_speed_kph = 30.0
    eta_minutes = (distance_km / avg_speed_kph) * 60

    print('rider', customer_coords[0], customer_coords[1])

    return render_template(
        'customer/track_order.html', 
        order=order, 
        distance=round(distance_km, 2),
        eta=round(eta_minutes)
    )