import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

os.environ["COQUI_TOS_AGREED"] = "1"
BASE = Path(__file__).parent
DIRS = {k: BASE / k for k in ["broll", "ai_assets", "audio", "subs", "output", "voices"]}
for d in DIRS.values():
    d.mkdir(exist_ok=True)

NICHES = ["finance-education"]
UPLOAD_COST = 1600
SEARCH_COST = 100
DAILY_QUOTA = 10000
OUTLIER_MULTIPLIER_MIN = 20.0
HORIZON_HOURS = 48
CPM_TIMEZONES = ["Europe/Rome", "America/New_York", "America/Los_Angeles"]
DB_PATH = BASE / "ysae.db"
CLIENT_SECRETS = str(BASE / "client_secret.json")
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
YT_CHANNEL_ID = os.environ.get("YT_CHANNEL_ID", "")

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]
