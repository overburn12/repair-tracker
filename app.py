"""Flask application for repair tracker."""
from flask import Flask, render_template, send_from_directory
from service import db_service

app = Flask(__name__)

# ------------------------------------------------------------------
# Pages
# ------------------------------------------------------------------

@app.route('/')
def index():
    """Render the main index page."""
    return render_template('index.html')


# ------------------------------------------------------------------
# API
# ------------------------------------------------------------------

# NOTE: any api routes please follow 'api/endpoint-name' naming scheme

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