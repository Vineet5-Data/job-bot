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
PRIMARY_GEMINI_MODEL = get_env_str("PRIMARY_GEMINI_MODEL", "gemini-3.7-flash")

# Tried in order. Newest first: within one family/tier the higher version is the
# stronger writer, and the free-tier quota is billed per MODEL per day
# (GenerateRequestsPerDayPerProjectPerModel, 20/day), so each extra entry buys a
# fresh 20-request budget instead of sharing one. Five models => ~100 free
# generations/day before OpenRouter is touched at all.
# Dropped 2026-08-27 after live probing returned 404 for both:
#   gemini-3-flash    -> never existed on v1beta
#   gemini-2.5-flash  -> "no longer available to new users" (retired)
# Each dead id cost a wasted round-trip per request before reaching OpenRouter.
GEMINI_FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]

OPENROUTER_API_KEY = get_env_str("OPENROUTER_API_KEY")
# Only reached once every Gemini model above is exhausted, so this chain is
# ordered by writing/reasoning quality rather than speed. Nemotron Ultra
# (55B active params) leads, then GLM, then Nemotron Super (12B active).
OPENROUTER_FALLBACK_MODELS = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "z-ai/glm-5.2:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
]

# A hung :free endpoint must not wedge the bot forever — a Telegram user waiting
# with no reply is worse than falling through to the next model.
LLM_TIMEOUT_SECONDS = int(get_env_str("LLM_TIMEOUT_SECONDS", "90"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

CV_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "cv_template.tex")
CL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "cl_template.tex")
MASTER_PROFILE_PATH = os.path.join(TEMPLATES_DIR, "master_profile.json")
