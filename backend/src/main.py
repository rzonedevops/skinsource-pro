import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

from src.models import db
from src.routes.ingredients import ingredients_bp
from src.routes.suppliers import suppliers_bp
from src.routes.procurement import procurement_bp
from src.routes.intelligence import intelligence_bp


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "static"))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")
default_db_path = os.path.join(os.path.dirname(__file__), "database")
os.makedirs(default_db_path, exist_ok=True)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(default_db_path, 'app.db')}",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

cors_origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()] or ["*"])

db.init_app(app)

# Register blueprints
app.register_blueprint(ingredients_bp, url_prefix="/api")
app.register_blueprint(suppliers_bp, url_prefix="/api")
app.register_blueprint(procurement_bp, url_prefix="/api")
app.register_blueprint(intelligence_bp, url_prefix="/api")

with app.app_context():
    db.create_all()


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)

    index_path = os.path.join(static_folder_path, "index.html")
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, "index.html")

    return "index.html not found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=os.getenv("FLASK_ENV") == "development")
