import os
import pyttsx3
import winsound
import threading
import queue
import time
import traceback
import logging

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, base_dir: str = "assets/audio"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.engine = pyttsx3.init()
        # Set property if needed (e.g. rate, volume)
        self.engine.setProperty('rate', 150)
        
        # Playback queue and worker
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._playback_worker, daemon=True)
        self.worker_thread.start()

    def _get_filepath(self, text: str) -> str:
        # Sanitize filename
        safe_text = "".join([c for c in text if c.isalnum() or c in (' ', '_', '-')]).strip()
        return os.path.join(self.base_dir, f"{safe_text}.wav")

    def generate_audio(self, text: str) -> str:
        """Generates audio file for the given text. Returns the filepath."""
        filepath = self._get_filepath(text)
        if not os.path.exists(filepath):
            try:
                # pyttsx3 save_to_file needs a runAndWait loop, but it can be tricky in main thread
                # We'll use a lock or just run it. 
                # Note: save_to_file is blocking usually.
                self.engine.save_to_file(text, filepath)
                self.engine.runAndWait()
                logger.debug(f"'{text}' 오디오 생성 완료: {filepath}")
            except Exception as e:
                logger.error(f"'{text}' 오디오 생성 오류: {e}", exc_info=True, 
                           extra={'text': text, 'filepath': filepath})
        return filepath

    def play_audio(self, text: str):
        """Queues the audio file for the given text."""
        self.queue.put([text])

    def play_sequence(self, texts: list[str]):
        """Queues a sequence of texts."""
        self.queue.put(texts)

    def _playback_worker(self):
        """Worker thread to play audio files sequentially."""
        while True:
            try:
                texts = self.queue.get()
                for text in texts:
                    filepath = self._get_filepath(text)
                    if os.path.exists(filepath):
                        try:
                            # File info for debugging
                            file_size = os.path.getsize(filepath)
                            
                            # SND_NODEFAULT: don't play default sound if file not found
                            # SND_NOSTOP: don't stop currently playing sound (though we are serial here)
                            winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                            logger.debug(f"'{text}' 재생 완료 ({file_size} bytes)")
                        except Exception as e:
                            logger.error(f"'{text}' 재생 오류: {e}", exc_info=True,
                                       extra={'filepath': filepath, 'exists': os.path.exists(filepath)})
                    else:
                        logger.warning(f"'{text}' 오디오 파일 없음: {filepath}")
                
                self.queue.task_done()
            except Exception as e:
                logger.error(f"재생 워커 오류: {e}", exc_info=True)
                time.sleep(1)
