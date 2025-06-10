# /food-delivery-app/app/routes/owner_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, abort
from app import db
from ..models.user import User
from ..models.shop import Shop
from ..models.item import Item
from ..models.order import Order
from .utils import login_required, role_required
from sqlalchemy.exc import IntegrityError
import uuid

owner_bp = Blueprint('owner_bp', __name__)

# Helper function to get the current owner's shop
def get_current_shop():
    user_id_bytes = uuid.UUID(session['user_id']).bytes
    # A user with an 'owner' role is guaranteed to have one shop
    shop = Shop.query.filter_by(owner_id=user_id_bytes).first()
    if not shop:
        abort(404, "Shop not found for the current user.")
    return shop

@owner_bp.route('/dashboard')
@login_required
@role_required('owner')
def dashboard():
    shop = get_current_shop()
    # Show orders that need action
    orders = Order.query.filter(
        Order.shop_id == shop.id,
        Order.order_status.in_(['pending', 'confirmed', 'preparing', 'ready_for_pickup'])
    ).order_by(Order.created_at.desc()).all()
    return render_template('owner/dashboard.html', orders=orders, shop_name=shop.name)

@owner_bp.route('/order/update/<order_uuid>', methods=['POST'])
@login_required
@role_required('owner')
def update_order_status(order_uuid):
    shop = get_current_shop()
    order_id_bytes = uuid.UUID(order_uuid).bytes
    order = Order.query.get(order_id_bytes)
    
    # Ensure the order belongs to the owner's shop
    if not order or order.shop_id != shop.id:
        flash("Order not found or you don't have permission to modify it.", 'danger')
        return redirect(url_for('owner_bp.dashboard'))

    new_status = request.form.get('status')
    if new_status in ['confirmed', 'preparing', 'ready_for_pickup']:
        order.order_status = new_status
        db.session.commit()
        flash(f"Order #{str(order.get_uuid())[:8]} status updated to '{new_status}'.", 'success')
    else:
        flash("Invalid status update.", 'danger')
        
    return redirect(url_for('owner_bp.dashboard'))


@owner_bp.route('/items')
@login_required
@role_required('owner')
def manage_items():
    shop = get_current_shop()
    items = Item.query.filter_by(shop_id=shop.id).order_by(Item.name).all()
    return render_template('owner/item_list.html', items=items, shop_name=shop.name)


@owner_bp.route('/items/new', methods=['GET', 'POST'])
@login_required
@role_required('owner')
def add_item():
    if request.method == 'POST':
        shop = get_current_shop()
        new_item = Item(
            id=uuid.uuid4().bytes,
            shop_id=shop.id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=request.form.get('price'),
            is_available='is_available' in request.form
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f"'{new_item.name}' has been added to your menu.", 'success')
        return redirect(url_for('owner_bp.manage_items'))
        
    return render_template('owner/item_form.html', form_title="Add New Item")

@owner_bp.route('/items/edit/<item_uuid>', methods=['GET', 'POST'])
@login_required
@role_required('owner')
def edit_item(item_uuid):
    shop = get_current_shop()
    item_id_bytes = uuid.UUID(item_uuid).bytes
    item = Item.query.get(item_id_bytes)

    if not item or item.shop_id != shop.id:
        flash("Item not found or you don't have permission.", 'danger')
        return redirect(url_for('owner_bp.manage_items'))

    if request.method == 'POST':
        item.name = request.form.get('name')
        item.description = request.form.get('description')
        item.price = request.form.get('price')
        item.is_available = 'is_available' in request.form
        db.session.commit()
        flash(f"'{item.name}' has been updated.", 'success')
        return redirect(url_for('owner_bp.manage_items'))

    return render_template('owner/item_form.html', item=item, form_title="Edit Item")

@owner_bp.route('/items/delete/<item_uuid>', methods=['POST'])
@login_required
@role_required('owner')
def delete_item(item_uuid):
    shop = get_current_shop()
    item_id_bytes = uuid.UUID(item_uuid).bytes
    item = Item.query.get(item_id_bytes)

    if not item or item.shop_id != shop.id:
        flash("Item not found or you don't have permission.", 'danger')
        return redirect(url_for('owner_bp.manage_items'))

    try:
        db.session.delete(item)
        db.session.commit()
        flash(f"'{item.name}' has been deleted.", 'success')
    except IntegrityError:
        db.session.rollback()
        flash(f"Cannot delete '{item.name}' because it is part of one or more past orders.", 'danger')
    
    return redirect(url_for('owner_bp.manage_items'))