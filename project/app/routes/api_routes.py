# /food-delivery-app/app/routes/api_routes.py
from flask import Blueprint, request, jsonify, session
from app import db
from ..models.user import User
from .utils import login_required
import uuid

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/update-location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    if not data or 'lat' not in data or 'lng' not in data:
        return jsonify({'status': 'error', 'message': 'Missing location data'}), 400

    try:
        user_id_bytes = uuid.UUID(session['user_id']).bytes
        user = User.query.get(user_id_bytes)
        if user:
            user.current_lat = data['lat']
            user.current_lng = data['lng']
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Location updated'})
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500