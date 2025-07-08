#!/usr/bin/env python3

"""
Enhanced Transcription Module for Glyph.
Supports both local Whisper models and OpenAI API transcription.
"""

import whisper
import scipy.io.wavfile
import tempfile
import os
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Tuple
import openai
from openai import OpenAI

from utils import SAMPLE_RATE, verbose_print
from transcription_config import get_transcription_config, TranscriptionMethod
from ui_helpers import show_error_message, show_warning_message

# Global model cache for local Whisper
_whisper_model = None
_current_model_name = None

class TranscriptionError(Exception):
    """Custom exception for transcription errors."""
    pass

class TranscriptionService:
    """Service class for handling both local and API-based transcription."""
    
    def __init__(self):
        self.config = get_transcription_config()
        self._openai_client = None
    
    def _get_openai_client(self) -> Optional[OpenAI]:
        """Get or create OpenAI client."""
        if self._openai_client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise TranscriptionError("OpenAI API key not found in environment variables")
            
            try:
                self._openai_client = OpenAI(api_key=api_key)
                verbose_print("✅ OpenAI client initialized")
            except Exception as e:
                raise TranscriptionError(f"Failed to initialize OpenAI client: {e}")
        
        return self._openai_client
    
    def _load_local_whisper_model(self, model_name: str):
        """Load and cache local Whisper model."""
        global _whisper_model, _current_model_name
        
        if _whisper_model is None or _current_model_name != model_name:
            verbose_print(f"Loading local Whisper model '{model_name}' (this may take a moment)...")
            try:
                _whisper_model = whisper.load_model(model_name)
                _current_model_name = model_name
                verbose_print(f"✅ Whisper model '{model_name}' loaded successfully")
            except Exception as e:
                raise TranscriptionError(f"Failed to load Whisper model '{model_name}': {e}")
        
        return _whisper_model
    
    def _transcribe_local(self, audio_data, language: str = "auto") -> str:
        """Transcribe using local Whisper model."""
        model_name = self.config.get_local_whisper_model()
        model = self._load_local_whisper_model(model_name)
        
        # Create temporary wav file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            try:
                # Write audio data to temporary file
                scipy.io.wavfile.write(temp_file.name, SAMPLE_RATE, audio_data)
                
                # Transcribe with language setting
                transcription_options = {}
                if language != "auto":
                    transcription_options["language"] = language
                
                verbose_print(f"🎯 Transcribing with local model '{model_name}'...")
                result = model.transcribe(temp_file.name, **transcription_options)
                
                transcript = result["text"].strip()
                verbose_print(f"✅ Local transcription completed: {len(transcript)} characters")
                
                return transcript
                
            except Exception as e:
                raise TranscriptionError(f"Local transcription failed: {e}")
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def _transcribe_openai_api(self, audio_data, language: str = "auto") -> str:
        """Transcribe using OpenAI API."""
        client = self._get_openai_client()
        model_name = self.config.get_openai_model()
        
        # Create temporary wav file for API upload
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            try:
                # Write audio data to temporary file
                scipy.io.wavfile.write(temp_file.name, SAMPLE_RATE, audio_data)
                
                verbose_print(f"🌐 Transcribing with OpenAI API model '{model_name}'...")
                
                # Prepare API call parameters
                transcription_params = {
                    "model": model_name,
                    "file": open(temp_file.name, "rb"),
                    "response_format": "text"
                }
                
                # Add language if specified
                if language != "auto":
                    transcription_params["language"] = language
                
                # Call OpenAI API
                response = client.audio.transcriptions.create(**transcription_params)
                
                # Handle response
                if isinstance(response, str):
                    transcript = response.strip()
                else:
                    transcript = str(response).strip()
                
                verbose_print(f"✅ OpenAI API transcription completed: {len(transcript)} characters")
                
                return transcript
                
            except openai.APIError as e:
                if "insufficient_quota" in str(e):
                    raise TranscriptionError("OpenAI API quota exceeded. Please check your billing.")
                elif "invalid_api_key" in str(e):
                    raise TranscriptionError("Invalid OpenAI API key. Please check your configuration.")
                else:
                    raise TranscriptionError(f"OpenAI API error: {e}")
            except Exception as e:
                raise TranscriptionError(f"OpenAI API transcription failed: {e}")
            finally:
                # Clean up temporary file
                try:
                    if 'transcription_params' in locals() and 'file' in transcription_params:
                        transcription_params['file'].close()
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def transcribe(self, audio_data, method: Optional[TranscriptionMethod] = None, language: str = "auto") -> str:
        """
        Transcribe audio data using the specified or configured method.
        
        Args:
            audio_data: Audio data array
            method: Transcription method ("local" or "openai_api"). If None, uses configured default.
            language: Language code or "auto" for automatic detection
            
        Returns:
            str: Transcribed text
            
        Raises:
            TranscriptionError: If transcription fails
        """
        if method is None:
            method = self.config.get_transcription_method()
        
        verbose_print(f"🎙️ Starting transcription with method: {method}")
        
        try:
            if method == "local":
                return self._transcribe_local(audio_data, language)
            elif method == "openai_api":
                return self._transcribe_openai_api(audio_data, language)
            else:
                raise TranscriptionError(f"Unknown transcription method: {method}")
                
        except TranscriptionError as e:
            # Try fallback to local if API method failed
            if method == "openai_api":
                verbose_print(f"⚠️ OpenAI API failed: {e}")
                verbose_print("🔄 Falling back to local Whisper...")
                show_warning_message("OpenAI API failed, falling back to local Whisper")
                try:
                    return self._transcribe_local(audio_data, language)
                except Exception as fallback_error:
                    raise TranscriptionError(f"Both API and local transcription failed. API error: {e}, Local error: {fallback_error}")
            else:
                raise
        except Exception as e:
            raise TranscriptionError(f"Unexpected error during transcription: {e}")
    
    def test_transcription_method(self, method: TranscriptionMethod) -> Tuple[bool, str]:
        """
        Test if a transcription method is working properly.
        
        Args:
            method: The transcription method to test
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if method == "local":
                model_name = self.config.get_local_whisper_model()
                self._load_local_whisper_model(model_name)
                return True, f"✅ Local Whisper model '{model_name}' is working"
                
            elif method == "openai_api":
                client = self._get_openai_client()
                # Test with a minimal API call (list models)
                try:
                    models = client.models.list()
                    return True, "✅ OpenAI API connection is working"
                except Exception as e:
                    return False, f"❌ OpenAI API test failed: {e}"
            else:
                return False, f"❌ Unknown method: {method}"
                
        except Exception as e:
            return False, f"❌ Test failed: {e}"

# Global transcription service instance
_transcription_service = None

def get_transcription_service() -> TranscriptionService:
    """Get or create the global transcription service instance."""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service

def transcribe_audio(audio_data, method: Optional[TranscriptionMethod] = None, language: str = "auto") -> Optional[str]:
    """
    Transcribe audio data using the configured or specified method.
    
    This is a convenience function that maintains compatibility with existing code.
    
    Args:
        audio_data: Audio data array
        method: Transcription method to use (None for default)
        language: Language for transcription
        
    Returns:
        str: Transcribed text, or None if transcription failed
    """
    try:
        service = get_transcription_service()
        return service.transcribe(audio_data, method, language)
    except TranscriptionError as e:
        show_error_message("❌ Transcription failed", str(e))
        return None
    except Exception as e:
        show_error_message("❌ Unexpected transcription error", str(e))
        return None

def save_transcript(transcript: str, filename_prefix: str = "transcript") -> Optional[str]:
    """
    Save transcript to file with timestamp.
    
    Args:
        transcript: The transcribed text
        filename_prefix: Prefix for the filename
        
    Returns:
        str: Path to saved file, or None if saving failed
    """
    try:
        # Create transcripts directory
        transcripts_dir = Path("transcripts")
        transcripts_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{filename_prefix}_{timestamp}.txt"
        filepath = transcripts_dir / filename
        
        # Save transcript
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        verbose_print(f"💾 Transcript saved to: {filepath}")
        return str(filepath)
        
    except Exception as e:
        verbose_print(f"❌ Failed to save transcript: {e}")
        return None

def test_all_transcription_methods() -> None:
    """Test all available transcription methods and show results."""
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from ui_helpers import GLYPH_PRIMARY, GLYPH_SUCCESS, GLYPH_ERROR
    
    console = Console()
    service = get_transcription_service()
    
    # Test results table
    table = Table(show_header=True, box=box.HEAVY, border_style=GLYPH_PRIMARY)
    table.add_column("Method", style="bold white", width=15)
    table.add_column("Status", style="bold", width=20)
    table.add_column("Details", style=GLYPH_PRIMARY, width=40)
    
    methods = [("local", "Local Whisper"), ("openai_api", "OpenAI API")]
    
    for method, display_name in methods:
        success, message = service.test_transcription_method(method)
        status_style = GLYPH_SUCCESS if success else GLYPH_ERROR
        status_text = "✅ Working" if success else "❌ Failed"
        
        table.add_row(
            display_name,
            f"[{status_style}]{status_text}[/{status_style}]",
            message
        )
    
    console.print("\n🧪 Transcription Method Test Results:")
    console.print(table)

# Backward compatibility - load Whisper model function
def load_whisper_model():
    """Load Whisper model (backward compatibility)."""
    service = get_transcription_service()
    config = service.config
    
    if config.get_transcription_method() == "local":
        model_name = config.get_local_whisper_model()
        return service._load_local_whisper_model(model_name)
    else:
        verbose_print("⚠️ load_whisper_model() called but using OpenAI API method")
        return None

if __name__ == "__main__":
    # Test the transcription system
    test_all_transcription_methods()