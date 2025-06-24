import sounddevice as sd
import numpy as np
from pynput import keyboard
import threading
import time
import sys
from utils import SAMPLE_RATE, CHANNELS, DEVICE_INDEX, SPINNER_FRAMES, verbose_print

class AudioRecorder:
    def __init__(self):
        self.frames = []
        self.stream = None
        self.recording = False
        
    def audio_callback(self, indata, frames_count, time_info, status):
        if status:
            print(f"⚠️ {status}", flush=True)
        if self.recording:
            self.frames.append(indata.copy())
    
    def start_recording(self, message="🎙️ Recording... Hold SPACEBAR to speak."):
        self.frames = []
        self.recording = True
        self.stream = sd.InputStream(
            device=DEVICE_INDEX, 
            callback=self.audio_callback, 
            channels=CHANNELS, 
            samplerate=SAMPLE_RATE
        )
        self.stream.start()
        print(message)
    
    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
        if self.frames:
            audio_data = np.concatenate(self.frames, axis=0)
            return self.validate_audio(audio_data)
        else:
            verbose_print("No audio frames captured during recording")
            return None
    
    def validate_audio(self, audio_data):
        """Validate recorded audio for quality and length."""
        if audio_data is None or len(audio_data) == 0:
            verbose_print("Audio validation failed: No data")
            return None
        
        # Check minimum duration (at least 0.5 seconds)
        duration_seconds = len(audio_data) / SAMPLE_RATE
        if duration_seconds < 0.5:
            verbose_print(f"Audio too short: {duration_seconds:.2f}s (minimum 0.5s)")
            return None
        
        # Check for silence (very low amplitude)
        max_amplitude = np.max(np.abs(audio_data))
        if max_amplitude < 0.01:  # Threshold for silence detection
            verbose_print(f"Audio appears to be silent: max amplitude {max_amplitude:.4f}")
            return None
        
        # Check for reasonable audio levels
        rms = np.sqrt(np.mean(audio_data**2))
        if rms < 0.005:  # Very quiet audio
            verbose_print(f"Audio very quiet: RMS {rms:.4f}")
            # Don't reject, but warn
        
        verbose_print(f"Audio validation passed: {duration_seconds:.2f}s, RMS {rms:.4f}, max {max_amplitude:.4f}")
        return audio_data

def run_voice_capture():
    print("⌨️ Hold SPACEBAR to record, release to stop...\n")
    
    recorder = AudioRecorder()
    recording_flag = {'value': False}
    start_time = time.time()
    spinner_thread = None
    
    def show_spinner():
        while recording_flag['value']:
            elapsed = int(time.time() - start_time)
            spinner = next(SPINNER_FRAMES)
            sys.stdout.write(f"\r🎙️ Recording... {spinner} {elapsed:02d}s")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def on_press_with_spinner(key):
        nonlocal spinner_thread, start_time
        if key == keyboard.Key.space and not recording_flag['value']:
            recording_flag['value'] = True
            start_time = time.time()
            recorder.start_recording()
            spinner_thread = threading.Thread(target=show_spinner)
            spinner_thread.start()

    def on_release_with_spinner(key):
        nonlocal spinner_thread
        if key == keyboard.Key.space and recording_flag['value']:
            recording_flag['value'] = False
            if spinner_thread:
                spinner_thread.join()
            print("\n⏹️ Stopped recording.")
            return False  # Stop listener
    
    with keyboard.Listener(on_press=on_press_with_spinner, on_release=on_release_with_spinner) as listener:
        listener.join()
    
    return recorder.stop_recording()

def run_enter_stop_capture():
    """Record audio until user presses Enter key - no keyboard hooks needed."""
    print("🎙️ Recording started... Press ENTER when finished speaking.")
    
    recorder = AudioRecorder()
    start_time = time.time()
    
    def show_recording_status():
        """Show animated recording status with timer."""
        while recorder.recording:
            elapsed = int(time.time() - start_time)
            spinner = next(SPINNER_FRAMES)
            sys.stdout.write(f"\r🎙️ Recording... {spinner} {elapsed:02d}s (Press ENTER to stop)")
            sys.stdout.flush()
            time.sleep(0.1)
    
    # Start recording immediately with custom message
    recorder.start_recording("")  # Empty message since we handle display separately
    
    # Start status display thread
    status_thread = threading.Thread(target=show_recording_status)
    status_thread.daemon = True
    status_thread.start()
    
    # Wait for Enter key press using standard input
    try:
        input()  # This will block until user presses Enter
    except (KeyboardInterrupt, EOFError):
        pass  # Handle Ctrl+C and EOF gracefully
    
    # Stop recording
    print("\n⏹️ Stopped recording.")
    return recorder.stop_recording()

def run_simple_record():
    print("🎤 Starting 5-second recording...")
    duration = 5
    audio = sd.rec(int(SAMPLE_RATE * duration), samplerate=SAMPLE_RATE, channels=CHANNELS)
    sd.wait()
    return audio