import os

# Ensure compatibility between platform environment variables
if "SQLALCHEMY_DATABASE_URI" in os.environ and "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = os.environ["SQLALCHEMY_DATABASE_URI"]

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret')
url = os.environ.get("DATABASE_URL") or "sqlite:///database.db"
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql://", 1)
SQLALCHEMY_DATABASE_URI = url
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
