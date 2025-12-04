import os
import pyttsx3
import winsound
import threading

class TTSService:
    def __init__(self, base_dir: str = "assets/audio"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.engine = pyttsx3.init()
        # Set property if needed (e.g. rate, volume)
        self.engine.setProperty('rate', 150)

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
                print(f"Generated audio for '{text}': {filepath}")
            except Exception as e:
                print(f"Error generating audio for '{text}': {e}")
        return filepath

    def play_audio(self, text: str):
        """Plays the audio file for the given text asynchronously."""
        filepath = self._get_filepath(text)
        if os.path.exists(filepath):
            try:
                # SND_FILENAME: filename is passed
                # SND_ASYNC: play asynchronously
                winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"Error playing audio '{text}': {e}")
        else:
            print(f"Audio file not found for '{text}': {filepath}")
            # Fallback: try to generate and play? Or just log.
            # self.generate_audio(text)
            
    def play_sequence(self, texts: list[str]):
        """Plays a sequence of texts. Note: winsound.SND_ASYNC interrupts previous sound.
        To play sequentially, we need to wait or use synchronous play in a thread."""
        
        def _play():
            for text in texts:
                filepath = self._get_filepath(text)
                if os.path.exists(filepath):
                    try:
                        # SND_NODEFAULT: don't play default sound if file not found
                        winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                    except Exception as e:
                        print(f"Error playing sequence '{text}': {e}")
        
        threading.Thread(target=_play, daemon=True).start()
