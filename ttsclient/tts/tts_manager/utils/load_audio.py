import os
import traceback
import librosa


def load_audio(file, sr):
    try:
        file = clean_path(file)
        if not os.path.exists(file):
            raise RuntimeError("You input a wrong audio path that does not exist, please fix it!")

        # librosa.load will handle loading, down-mixing to mono and resampling the audio
        audio, _ = librosa.load(file, sr=sr, mono=True)  # librosaは元のデータ型に寄らず、floatで返す決まり。
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"Failed to load audio: {e}")

    return audio


def clean_path(path_str: str):
    if path_str.endswith(("\\", "/")):
        return clean_path(path_str[0:-1])
    path_str = path_str.replace("/", os.sep).replace("\\", os.sep)
    return path_str.strip(" ").strip("'").strip("\n").strip('"').strip(" ").strip("\u202a")
