import os
from app import create_app, socketio

# Pick config based on environment variable, default to 'development'
config_name = os.environ.get('FLASK_ENV', 'development')

# Create the Flask application
app = create_app(config_name)


if __name__ == '__main__':
    print("=" * 50)
    print("  EventHub is running!")
    print("  Open: http://127.0.0.1:5000")
    print("=" * 50)

    # Use socketio.run instead of app.run to support real-time features
    socketio.run(
        app,
        host='0.0.0.0',   # Accept connections from any IP
        port=5000,
        debug=True
    )
