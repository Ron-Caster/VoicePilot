import app_open
import mouse_click as click
import threading
import sounddevice as sd
import tempfile
import scipy.io.wavfile
from groq import Groq
import goto

client = Groq()

SAMPLE_RATE = 16000
DURATION = 5  # seconds

def record_audio():
    print("🎙️  Speak now...")
    audio = sd.rec(int(SAMPLE_RATE * DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    return audio

def transcribe(audio):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        scipy.io.wavfile.write(f.name, SAMPLE_RATE, audio)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as fh:
            transcription = client.audio.transcriptions.create(
                file=(tmp_path, fh.read()),
                model="whisper-large-v3-turbo",
                temperature=0,
                response_format="verbose_json",
            )
        if isinstance(transcription, dict):
            return transcription.get("text", "")
        return getattr(transcription, "text", None) or str(transcription)
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return ""

# (Note: final `handle_command` with goto support is defined later.)

def main():
    print("🧠 VoicePilot (Whisper STT) Ready. Say: 'open app' or 'click word'")
    while True:
        audio = record_audio()
        text = transcribe(audio)
        if text:
            print(f"🗣️  You said: {text}")
            if not handle_command(text):
                break
        else:
            print("❌ Could not understand. Try again.")

# Modified click.py integration
def main_threaded_click(word):
    thread = threading.Thread(target=click_entry, args=(word,))
    thread.start()

def click_entry(word):
    scale = click.get_windows_scaling()
    click.pyautogui.screenshot(click.SCREENSHOT_PATH)
    words_phys, _ = click.extract_words_physical(click.SCREENSHOT_PATH, click.TESSDATA_FOLDER)
    words_logical = [
        (txt, x0/scale, y0/scale, x1/scale, y1/scale)
        for (txt, x0, y0, x1, y1) in words_phys
    ]
    click.click_word(word, words_logical)

def handle_command(command):
    command = command.strip().lower()
    if command.startswith("open "):
        app_name = command.replace("open ", "")
        print(app_open.perform_action(app_name))
    elif command.startswith("click "):
        keyword = command.replace("click ", "")
        click.main_threaded(keyword)
    # Add this new section for "go to"
    elif command.startswith("go to "):
        site_query = command.replace("go to ", "", 1).strip()
        goto.open_website_threaded(site_query)
    elif command in ["exit", "quit"]:
        print("👋 Exiting VoicePilot.")
        return False
    else:
        print("🤖 Unknown command. Try: 'open notepad', 'click submit', or 'go to youtube'")
    return True

click.main_threaded = main_threaded_click

if __name__ == "__main__":
    main()
