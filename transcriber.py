from faster_whisper import WhisperModel
import config, assets

def generate_subs(audio_path=config.DIRS["audio"] / "voice.wav", out_path=config.DIRS["subs"] / "subs.ass"):
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True, language="it")
    
    words_with_ms = []
    for segment in segments:
        for word in segment.words:
            words_with_ms.append((word.word.strip(), int(word.start * 1000)))
            
    return assets.build_karaoke_ass(words_with_ms, out_path)
