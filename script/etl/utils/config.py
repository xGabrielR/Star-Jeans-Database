import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_NAME = os.getenv('DB_NAME')
DB_HOST = os.getenv('DB_HOST')
DB_PASS = os.getenv('DB_PASS')
DB_USER = os.getenv('DB_USER')
DB_PORT = os.getenv('DB_PORT')