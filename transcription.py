import whisper
import scipy.io.wavfile
import tempfile
import os
from datetime import datetime
from pathlib import Path
from utils import SAMPLE_RATE, WHISPER_MODEL, verbose_print

# Global model variable for caching
_whisper_model = None

def load_whisper_model():
    """
    Load Whisper model once and cache it for reuse.
    This prevents reloading the model on every transcription.
    """
    global _whisper_model
    if _whisper_model is None:
        verbose_print(f"Loading Whisper model '{WHISPER_MODEL}' (this may take a moment)...")
        _whisper_model = whisper.load_model(WHISPER_MODEL)
        verbose_print(f"Whisper model '{WHISPER_MODEL}' loaded successfully")
    return _whisper_model

def transcribe_audio(audio_data):
    """
    Transcribe audio data using the configured Whisper model.
    
    Args:
        audio_data: Audio data array
        
    Returns:
        Transcribed text string or None if failed
    """
    if audio_data is None or len(audio_data) == 0:
        return None
    
    try:
        # Load the model (cached after first use)
        model = load_whisper_model()
        
        # Create temporary file for audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            scipy.io.wavfile.write(tmpfile.name, SAMPLE_RATE, audio_data)
            verbose_print(f"Saved audio to temporary file: {tmpfile.name}")
            
            # Transcribe with better parameters for accuracy
            verbose_print("Starting Whisper transcription with optimized parameters...")
            result = model.transcribe(
                tmpfile.name,
                language="en",  # Specify English for better accuracy
                task="transcribe",  # Explicit task specification
                temperature=0.0,  # Lower temperature for more consistent results
                best_of=2,  # Try multiple decoding attempts for better accuracy
                beam_size=5,  # Use beam search for better quality
                fp16=False  # Use fp32 for better accuracy on CPU
            )
            verbose_print("Whisper transcription completed")
            
            # Clean up temporary file
            try:
                os.unlink(tmpfile.name)
                verbose_print(f"Cleaned up temporary file: {tmpfile.name}")
            except:
                pass  # Ignore cleanup errors
                
            return result['text'].strip()
            
    except Exception as e:
        verbose_print(f"Transcription error: {e}")
        return None

def save_transcript(text):
    if not text or text.strip() == "":
        verbose_print("No transcript text to save")
        return None
        
    Path("transcripts").mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"transcripts/{timestamp}.txt"
    
    with open(filename, "w") as f:
        f.write(text.strip())
    
    verbose_print(f"Transcript saved to {filename}")
    return filename