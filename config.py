import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()

class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-secret-key-change-in-prod-88371923')
    
    # Database connection parameters
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'LibraryDB')

    # Business logic defaults
    CURRENCY_SYMBOL = os.environ.get('CURRENCY_SYMBOL', '₹')
    FINE_PER_DAY = float(os.environ.get('FINE_PER_DAY', 5.00))
    DEFAULT_LOAN_DAYS = int(os.environ.get('DEFAULT_LOAN_DAYS', 14))
