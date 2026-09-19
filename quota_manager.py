import datetime, zoneinfo, json, config

QUOTA_FILE = config.BASE / "quota.json"

def get_pt_date():
    return datetime.datetime.now(zoneinfo.ZoneInfo("America/Los_Angeles")).date().isoformat()

def _load():
    if QUOTA_FILE.exists():
        try:
            return json.loads(QUOTA_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"date": get_pt_date(), "units": 0}

def _save(data):
    QUOTA_FILE.write_text(json.dumps(data))

class QuotaExhausted(Exception): pass

def spend(units: int):
    used = _load()
    today = get_pt_date()
    if used.get("date") != today:
        used = {"date": today, "units": 0}
        
    if used["units"] + units > config.DAILY_QUOTA:
        raise QuotaExhausted(f"Quota esaurita: {used['units']}/{config.DAILY_QUOTA}")
        
    used["units"] += units
    _save(used)
