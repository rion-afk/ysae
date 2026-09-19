import config

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Poppins,90,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,6,0,2,60,60,300,1
"""

def download_broll(query: str, dest=config.DIRS["broll"]):
    import requests
    if not config.PEXELS_API_KEY:
        print("⚠️ Nessuna Pexels API Key configurata. B-Roll saltato.")
        return
        
    r = requests.get("https://api.pexels.com/videos/search",
                     params={"query": query, "orientation": "portrait", "per_page": 8},
                     headers={"Authorization": config.PEXELS_API_KEY}, timeout=30)
    r.raise_for_status()
    
    for i, video in enumerate(r.json().get("videos", [])):
        for f in video.get("video_files", []):
            if f["height"] >= 1920 and f["width"] >= 1080:
                (dest / f"broll_{i}.mp4").write_bytes(requests.get(f["link"], timeout=60).content)
                break

def build_karaoke_ass(words_with_ms: list[tuple[str, int]], out=config.DIRS["subs"] / "subs.ass"):
    events = []
    for w, t in words_with_ms:
        events.append((w, t))
    body = ASS_HEADER
    for i in range(0, len(events), 4):
        chunk = events[i:i+4]
        start = chunk[0][1] / 1000
        end = (chunk[-1][1] + 800) / 1000
        ks = "".join(f"{{\\k{int((chunk[j+1][1]-chunk[j][1])/10) if j+1<len(chunk) else 30}}}{w} "
                     for j, (w, _) in enumerate(chunk))
        body += f"Dialogue: 0,{_ts(start)},{_ts(end)},Karaoke,,0,0,0,,{ks}\n"
    out.write_text(body, encoding="utf-8")
    return out

def _ts(s): 
    h, rem = divmod(s, 3600); m, sec = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{sec:05.2f}"

def human_in_the_loop_prompt(script: dict, out=config.BASE / "PROMPT_PER_AI.txt"):
    prompt = f"""HYPE-REALISTIC 9:16 ASSETS — genera e salva in {config.DIRS['ai_assets']}/

Ecco i prompt visivi generati dall'AI:
{script['visual_shots']}

Regole: photorealistic, cinematic lighting, 1080x1920, niente testo nell'immagine.
Nominare i file: SHOT_01.png, ecc.
"""
    out.write_text(prompt, encoding="utf-8")
    return out

def assets_ready() -> bool:
    return any(config.DIRS["ai_assets"].glob("SHOT_*"))
