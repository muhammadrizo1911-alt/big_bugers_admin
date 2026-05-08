import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8655163628:AAH-jfQj3WrBwA_0BtcR64WSyRbtcYqFOqk")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "6917006135").split(",")))

# MySQL sozlamalari
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "ck540806_test")
DB_PASSWORD = os.getenv("DB_PASSWORD", "test")
DB_NAME = os.getenv("DB_NAME", "ck540806_test")
