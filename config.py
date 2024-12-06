import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_default_secret_key')
    MYSQL_HOST = os.getenv('MYSQLHOST')
    MYSQL_USER = os.getenv('MYSQLUSER')
    MYSQL_PASSWORD = os.getenv('MYSQLPASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DATABASE')
    MYSQL_PORT = int(os.getenv('MYSQLPORT', 3306))
