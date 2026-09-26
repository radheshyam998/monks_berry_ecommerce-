import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///monksberry.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@monksberry.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@12345")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
