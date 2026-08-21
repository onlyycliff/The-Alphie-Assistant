import whisper


def get_model():
    """ Loads the necessary whisper model for transcribing audio"""
    try:
        model = whisper.load_model("medium")
        return model
    except Exception as e:
        return f"Unable to retrieve necessary model {e}"

def transcribe_audio(model, file_path: str) -> str:
    """Transcribes audio from the given file path using OpenAI's Whisper model."""
    if isinstance(model, str):
        return f"Whisper model is not available"
    try:
        result = model.transcribe(file_path)
        if result['text'].strip() == " ":
            return "[no speech detected]"
        else:
            return result['text']
    except FileNotFoundError as e:
        return f'Unable to find the necessary file {e}'
