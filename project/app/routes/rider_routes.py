from flask import Blueprint, render_template, redirect, url_for, flash, session
from app import db
from ..models.order import Order
from .utils import login_required, role_required
import uuid

rider_bp = Blueprint('rider_bp', __name__)

@rider_bp.route('/dashboard')
@login_required
@role_required('rider')
def dashboard():
    rider_id_bytes = uuid.UUID(session['user_id']).bytes
    
    active_delivery = Order.query.filter_by(rider_id=rider_id_bytes, order_status='picked_up').first()
    
    available_orders = []
    if not active_delivery:
        available_orders = Order.query.filter_by(order_status='ready_for_pickup').order_by(Order.created_at.asc()).all()

    return render_template('rider/dashboard.html', active_delivery=active_delivery, available_orders=available_orders)

@rider_bp.route('/orders/accept/<order_uuid>', methods=['POST'])
@login_required
@role_required('rider')
def accept_delivery(order_uuid):
    rider_id_bytes = uuid.UUID(session['user_id']).bytes

    if Order.query.filter_by(rider_id=rider_id_bytes, order_status='picked_up').first():
        flash("You already have an active delivery. Please complete it first.", 'warning')
        return redirect(url_for('rider_bp.dashboard'))
    
    order_id_bytes = uuid.UUID(order_uuid).bytes
    order = Order.query.get(order_id_bytes)

    if order and order.order_status == 'ready_for_pickup':
        order.rider_id = rider_id_bytes
        order.order_status = 'picked_up'
        db.session.commit()
        flash("Delivery accepted! Please proceed to the shop for pickup.", 'success')
    else:
        flash("This delivery is no longer available.", 'danger')
        
    return redirect(url_for('rider_bp.dashboard'))

@rider_bp.route('/orders/complete/<order_uuid>', methods=['POST'])
@login_required
@role_required('rider')
def complete_delivery(order_uuid):
    rider_id_bytes = uuid.UUID(session['user_id']).bytes
    order_id_bytes = uuid.UUID(order_uuid).bytes
    order = Order.query.get(order_id_bytes)

    if order and order.rider_id == rider_id_bytes and order.order_status == 'picked_up':
        order.order_status = 'delivered'
        db.session.commit()
        flash("Delivery marked as complete. Thank you!", 'success')
    else:
        flash("Could not update delivery status.", 'danger')

    return redirect(url_for('rider_bp.dashboard'))