"""Flask application for repair tracker."""
from flask import Flask, render_template, send_from_directory, jsonify, request
from service import db_service

app = Flask(__name__)

# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    """Render the main index page."""
    return render_template('index.html')


@app.route('/order', methods=['GET'])
def order():
    """Render the order page."""
    return render_template('order.html')


@app.route('/update', methods=['GET'])
def update():
    """Render the update database page."""
    return render_template('update.html')


@app.route('/settings', methods=['GET'])
def settings():
    """Render the settings page."""
    return render_template('settings.html')


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------

# NOTE: any api routes please follow 'api/endpoint-name' naming scheme


@app.route('/api/statuses', methods=['GET'])
def api_get_statuses():
    """Get all statuses from the database."""
    try:
        statuses = db_service.get_all_statuses()
        return jsonify(statuses), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-status', methods=['POST'])
def api_add_status():
    """Add a new status to the database."""
    try:
        data = request.get_json()
        status_name = data.get('status')

        if not status_name or not status_name.strip():
            return jsonify({'success': False, 'message': 'Status name is required'}), 400

        result = db_service.add_status(status_name.strip())
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/update-status/<status_key>', methods=['PUT'])
def api_update_status(status_key):
    """Update a status name by its key (e.g., 'ST-1')."""
    try:
        data = request.get_json()
        new_name = data.get('status')

        if not new_name or not new_name.strip():
            return jsonify({'success': False, 'message': 'Status name is required'}), 400

        result = db_service.update_status(status_key, new_name.strip())
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete-status/<status_key>', methods=['DELETE'])
def api_delete_status(status_key):
    """Delete a status by its key (e.g., 'ST-1')."""
    try:
        result = db_service.delete_status(status_key)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/assignees', methods=['GET'])
def api_get_assignees():
    """Get all assignees from the database."""
    try:
        assignees = db_service.get_all_assignees()
        return jsonify(assignees), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add-assignee', methods=['POST'])
def api_add_assignee():
    """Add a new assignee to the database."""
    try:
        data = request.get_json()
        assignee_name = data.get('name')

        if not assignee_name or not assignee_name.strip():
            return jsonify({'success': False, 'message': 'Assignee name is required'}), 400

        result = db_service.add_assignee(assignee_name.strip())
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/update-assignee/<assignee_key>', methods=['PUT'])
def api_update_assignee(assignee_key):
    """Update an assignee name by its key (e.g., 'AS-1')."""
    try:
        data = request.get_json()
        new_name = data.get('name')

        if not new_name or not new_name.strip():
            return jsonify({'success': False, 'message': 'Assignee name is required'}), 400

        result = db_service.update_assignee(assignee_key, new_name.strip())
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/delete-assignee/<assignee_key>', methods=['DELETE'])
def api_delete_assignee(assignee_key):
    """Delete an assignee by its key (e.g., 'AS-1')."""
    try:
        result = db_service.delete_assignee(assignee_key)
        status_code = 200 if result['success'] else 400
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/repair-orders', methods=['GET'])
def api_get_repair_orders():
    """Get all repair orders from the database."""
    try:
        orders = db_service.get_all_repair_orders()
        return jsonify(orders), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/repair-units/<order_key>', methods=['GET'])
def api_get_repair_units(order_key):
    """Get all repair units for a given repair order key (e.g., 'RO-123')."""
    try:
        units = db_service.get_repair_units_by_order(order_key)
        return jsonify(units), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ------------------------------------------------------------------
# Misc
# ------------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    """Serve the favicon."""
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    # Initialize database before running the app
    print("Initializing database...")
    db_service.initialize()
    print("Database ready!")

    DEBUG_IT = True
    try:
        app.run(host='0.0.0.0', port=42069, debug=DEBUG_IT)
    finally:
        # Clean up database connections when app shuts down
        db_service.close()