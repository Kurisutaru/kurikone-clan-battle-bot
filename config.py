# config.py
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

config = {
    'DB_HOST': os.getenv('DB_HOST'),
    'DB_USER': os.getenv('DB_USER'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD'),
    'DB_NAME': os.getenv('DB_NAME'),
    'DB_PORT': int(os.getenv('DB_PORT')),
    'MAX_POOL_SIZE': int(os.getenv('MAX_POOL_SIZE')),
    'DISCORD_TOKEN': os.getenv('DISCORD_TOKEN'),
    'CATEGORY_CHANNEL_NAME': os.getenv('CATEGORY_CHANNEL_NAME'),
    'REPORT_CHANNEL_NAME': os.getenv('REPORT_CHANNEL_NAME'),
    'BOSS1_CHANNEL_NAME': os.getenv('BOSS1_CHANNEL_NAME'),
    'BOSS2_CHANNEL_NAME': os.getenv('BOSS2_CHANNEL_NAME'),
    'BOSS3_CHANNEL_NAME': os.getenv('BOSS3_CHANNEL_NAME'),
    'BOSS4_CHANNEL_NAME': os.getenv('BOSS4_CHANNEL_NAME'),
    'BOSS5_CHANNEL_NAME': os.getenv('BOSS5_CHANNEL_NAME'),
    'TL_SHIFTER_CHANNEL_NAME': os.getenv('TL_SHIFTER_CHANNEL_NAME'),
    'MESSAGE_DEFAULT_DELETE_AFTER': int(os.getenv('MESSAGE_DEFAULT_DELETE_AFTER')),
}