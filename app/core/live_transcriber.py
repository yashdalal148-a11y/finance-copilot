"""
Live Transcriber Daemon for the Live Interview Copilot.
Listens continuously, detects voice activity, chunks audio, and automatically triggers the Orchestrator.
"""

import io
import queue
import wave
import time
import logging
import threading
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

class LiveTranscriber:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.is_running = False
        self.audio_queue = queue.Queue()
        
        # Audio config
        self.sample_rate = 16000
        self.channels = 1
        
        # VAD config
        self.energy_threshold = 0.015  # Adjust based on mic sensitivity
        self.silence_duration_sec = 2.0  # Seconds of silence to trigger end of utterance
        self.min_recording_sec = 1.0     # Minimum length of utterance to process

        self._listener_thread: Optional[threading.Thread] = None
        self._processor_thread: Optional[threading.Thread] = None
        
        # Shared state for Streamlit
        self.latest_result = None
        self.status = "Idle"

    def start(self):
        """Starts the continuous transcription background threads."""
        if self.is_running:
            return
        
        try:
            import sounddevice as sd
        except ImportError:
            logger.error("sounddevice is not installed. Live Copilot cannot run.")
            self.status = "Error: Missing dependencies"
            return
            
        self.is_running = True
        self.status = "Listening..."
        self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._processor_thread = threading.Thread(target=self._process_loop, daemon=True)
        self._listener_thread.start()
        self._processor_thread.start()

    def stop(self):
        """Stops the daemon."""
        self.is_running = False
        self.status = "Stopped"

    def _listen_loop(self):
        """Continuously listens to microphone and chunks audio based on silence."""
        import sounddevice as sd
        
        chunk_duration = 0.1
        chunk_samples = int(self.sample_rate * chunk_duration)
        
        recording = []
        is_speaking = False
        silence_timer = 0.0

        try:
            with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, dtype='float32') as stream:
                while self.is_running:
                    data, _ = stream.read(chunk_samples)
                    rms = np.sqrt(np.mean(data**2))

                    if rms > self.energy_threshold:
                        is_speaking = True
                        silence_timer = 0.0
                        recording.append(data)
                    elif is_speaking:
                        silence_timer += chunk_duration
                        recording.append(data)
                        
                        if silence_timer >= self.silence_duration_sec:
                            # Utterance complete
                            is_speaking = False
                            
                            # Convert chunks to a single array
                            full_audio = np.concatenate(recording, axis=0)
                            recording = []
                            
                            duration = len(full_audio) / self.sample_rate
                            if duration >= self.min_recording_sec:
                                self.audio_queue.put(full_audio)
        except Exception as e:
            logger.error(f"LiveTranscriber listener failed: {e}")
            self.status = "Error: Audio Input Failed"
            self.is_running = False

    def _process_loop(self):
        """Processes completed audio chunks through the orchestrator."""
        while self.is_running:
            try:
                audio_array = self.audio_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            self.status = "Processing..."
            
            # Convert float32 numpy array to 16-bit PCM WAV bytes
            wav_bytes = self._numpy_to_wav(audio_array)
            
            # Run pipeline
            try:
                result = self.orchestrator.run(wav_bytes)
                if result.success and result.transcription and not result.transcription.is_empty:
                    self.latest_result = result
            except Exception as e:
                logger.error(f"LiveTranscriber pipeline failed: {e}")
                
            self.status = "Listening..."
            self.audio_queue.task_done()

    def _numpy_to_wav(self, audio_array: np.ndarray) -> bytes:
        """Converts float32 numpy array to WAV bytes."""
        audio_int16 = np.int16(audio_array * 32767)
        byte_io = io.BytesIO()
        with wave.open(byte_io, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(audio_int16.tobytes())
        return byte_io.getvalue()
