import os
from dotenv import load_dotenv

load_dotenv()

def get_env_str(key, default=""):
    val = os.getenv(key, default)
    return val.strip('"\'') if val else val

TELEGRAM_BOT_TOKEN = get_env_str("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_env_str("TELEGRAM_CHAT_ID")
if TELEGRAM_CHAT_ID:
    TELEGRAM_CHAT_ID = int(TELEGRAM_CHAT_ID)

GEMINI_API_KEY = get_env_str("GEMINI_API_KEY")
PRIMARY_GEMINI_MODEL = get_env_str("PRIMARY_GEMINI_MODEL", "gemini-3.6-flash")

OPENROUTER_API_KEY = get_env_str("OPENROUTER_API_KEY")
OPENROUTER_FALLBACK_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "z-ai/glm-5.2:free"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

CV_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "cv_template.tex")
CL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "cl_template.tex")
MASTER_PROFILE_PATH = os.path.join(TEMPLATES_DIR, "master_profile.json")
