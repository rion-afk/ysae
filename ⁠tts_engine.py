from TTS.api import TTS
import config

_model = None
def _tts():
    global _model
    if _model is None:
        _model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
    return _model

def narrate(script: dict, out_path=config.DIRS["audio"] / "voice.wav"):
    text = f"{script['hook']} {script['escalation']} {script['loop']}"
    _tts().tts_to_file(text=text, language="it",
                       speaker_wav=str(config.DIRS["voices"] / "me.wav"),
                       file_path=str(out_path), split_sentences=True)
    return out_path
