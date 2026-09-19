import datetime, config, db

class DataNotReady(Exception): pass

def retention_curve(yt_analytics, video_id, channel_id, ts) -> dict[float, float]:
    start_date = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    end_date = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    
    res = yt_analytics.reports().query(
        ids=f"channel=={channel_id}", startDate=start_date,
        endDate=end_date, metrics="audienceWatchRatio",
        dimensions="elapsedVideoTimeRatio", filters=f"video=={video_id}").execute()
    
    return {float(r[0]): float(r[1]) for r in res.get("rows", [])}

def evaluate(yt_analytics, video_id, channel_id, ts):
    curve = retention_curve(yt_analytics, video_id, channel_id, ts)
    if not curve:
        raise DataNotReady("Dati Analytics non ancora elaborati da Google.")
        
    closest_k = min(curve.keys(), key=lambda x: abs(x - 0.06))
    r3 = curve[closest_k]
    avg = sum(curve.values()) / len(curve)
    
    db.update_result(video_id, retention_3s=r3, retention_avg=avg)
    exp = db.all("video_id=?", (video_id,))[0]
    db.bandit_update(exp["hook_template"], success=r3 > 0.85)
