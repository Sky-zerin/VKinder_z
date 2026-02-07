import os
from dotenv import load_dotenv

load_dotenv()

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_USER_TOKEN = os.getenv("VK_USER_TOKEN")

if not VK_GROUP_TOKEN or not VK_USER_TOKEN:
    raise RuntimeError("Не заданы VK токены в .env")
