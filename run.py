from app import create_app, db
from flask import session, redirect, url_for

app = create_app()

@app.route('/')
def root_route():
    if 'user_id' in session:
        role = session.get('user_role')
        if role == 'customer':
            return redirect(url_for('customer_bp.dashboard'))
        elif role == 'owner':
            return redirect(url_for('owner_bp.dashboard'))
        elif role == 'rider':
            return redirect(url_for('rider_bp.dashboard'))
    return redirect(url_for('auth_bp.login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')