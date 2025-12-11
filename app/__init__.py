import os
from dotenv import load_dotenv
from flask import Flask
from config import config

# Load environment variables from .env file
load_dotenv()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Example of reading an API key from .env
    anam_api_key = os.getenv("ANAM_API_KEY")
    if anam_api_key:
        print("Anam API Key loaded successfully.")
    else:
        print("Anam API Key not found. Please check your .env file.")

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register Blueprints
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    # Root route
    @app.route('/')
    def hello_world():
        return "Hello, World!"

    # Health check
    @app.route('/health')
    def health():
        return {'status': 'ok', 'app': 'Comics Factory'}, 200

    return app
