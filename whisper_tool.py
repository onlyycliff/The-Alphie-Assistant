import logging

import whisper

logger = logging.getLogger(__name__)


def get_model():
    """Loads the necessary whisper model for transcribing audio, or None on failure."""
    try:
        return whisper.load_model("medium")
    except Exception as e:
        logger.error("Unable to load whisper model: %s", e)
        return None

def transcribe_audio(model, file_path: str) -> str | None:
    """Transcribes audio from the given file path using OpenAI's Whisper model.

    Returns None (instead of an error string) when transcription can't be
    performed, so callers don't accidentally forward an error message to the LLM
    as if it were user input.
    """
    if model is None:
        logger.error("Whisper model is not available.")
        return None
    try:
        result = model.transcribe(file_path)
        text = result['text'].strip()
        if text == "":
            return "[no speech detected]"
        return text
    except FileNotFoundError as e:
        logger.error("Unable to find the necessary file: %s", e)
        return None
