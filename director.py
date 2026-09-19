import subprocess, cv2, numpy as np, config

W, H = 1080, 1920

def get_duration(file_path) -> float:
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1",
         str(file_path).replace("\\", "/")],
        capture_output=True, text=True)
    return float(res.stdout.strip())

def smart_crop(src, dst, target=(H, W)):
    cap = cv2.VideoCapture(str(src))
    ok, frame = cap.read()
    if not ok: return
    
    h_src, w_src = frame.shape[:2]
    if h_src >= w_src:
        cap.release()
        subprocess.run(["ffmpeg", "-y", "-i", str(src), 
                        "-vf", f"scale={W}:{H},setsar=1", str(dst)], capture_output=True)
        return
        
    scale = w_src / 480.0
    crop_w_small = int(270 * (target[1] / target[0]))
    best_var, bx = -1, 0
    frame_idx = 0
    
    while True:
        ok, frame = cap.read()
        if not ok: break
        if frame_idx % 10 == 0:  # Fix: Ottimizzazione x10 CPU
            small = cv2.resize(frame, (480, 270))
            cols = np.var(small.astype(float), axis=(0, 2))
            for x in range(small.shape[1] - crop_w_small):
                v = cols[x:x+crop_w_small].mean()
                if v > best_var:
                    best_var, bx = v, x
        frame_idx += 1
    cap.release()

    # Riapri solo per i metadati
    cap2 = cv2.VideoCapture(str(src))
    fps = cap2.get(cv2.CAP_PROP_FPS)
    cap2.release()
    
    # Fix: Clamp per evitare sforamento coordinate su ffmpeg
    crop_w_full = min(int(crop_w_small * scale), w_src)
    crop_x_full = min(int(bx * scale), w_src - crop_w_full)
    
    vf = f"crop={crop_w_full}:{h_src}:{crop_x_full}:0,scale={W}:{H},setsar=1"
    subprocess.run(["ffmpeg", "-y", "-i", str(src), "-vf", vf, "-r", str(fps), str(dst)], capture_output=True)

def ken_burns(img_path, out, duration=5):
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(img_path),
        "-vf", f"zoompan=z='min(zoom+0.0015,1.15)':d={duration*30}"
               f":x='iw/2-(iw/zoom/2)':y='ih/3':s={W}x{H},setsar=1",
        "-t", str(duration), "-pix_fmt", "yuv420p", str(out)], capture_output=True)

def compose(timeline: list[str], voice_wav, music_path, subs_ass, out_path):
    assert len(timeline) > 0, "Errore Critico: Nessuna clip video nella timeline."
    inputs = []
    for clip in timeline:
        inputs += ["-i", str(clip)]
    n = len(timeline)

    inputs += ["-i", str(voice_wav), "-stream_loop", "-1", "-i", str(music_path)]
    voice_dur = get_duration(voice_wav)
    subs_escaped = str(subs_ass).replace("\\", "/").replace(":", "\\:")

    fc = "".join(f"[{i}:v]scale={W}:{H},setsar=1,fps=30[v{i}];" for i in range(n))
    if n == 1:
        fc += "[v0]null[vraw];"
    else:
        fc += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vraw];"

    fc += f"[vraw]tpad=stop_mode=clone:stop_duration=120[vpad];" \
          f"[vpad]trim=0:{voice_dur},setpts=PTS-STARTPTS[vbase];"

    fc += f"""[vbase]subtitles='{subs_escaped}'[vout];
[{n}:a]atrim=0:{voice_dur},asplit=2[voice_trigger][voice_mix];
[{n+1}:a]volume=0.25[mus_raw];
[mus_raw][voice_trigger]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=300[mus_ducked];
[voice_mix][mus_ducked]amix=inputs=2:duration=first:normalize=0[aout]"""

    res = subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", fc,
                          "-map", "[vout]", "-map", "[aout]",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                          "-c:a", "aac", "-b:a", "192k",
                          str(out_path)], capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Errore composizione FFmpeg: {res.stderr}")
    return out_path
