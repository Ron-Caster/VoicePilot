import ctypes
import fitz           # pip install pymupdf
import pyautogui      # pip install pyautogui
import time
import os

# ——— USER CONFIG ——————————————————————————————————————————————————
TESSDATA_FOLDER = r"C:\Program Files\Tesseract-OCR\tessdata"
SCREENSHOT_PATH = "screen.png"
OCR_DPI         = 300   # bump up small‑text accuracy
# ————————————————————————————————————————————————————————————————

def get_windows_scaling():
    """Return DPI scaling factor (e.g. 1.25 for 125%)."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()
    dpi = ctypes.windll.user32.GetDpiForSystem()
    return dpi / 96.0

def extract_words_physical(image_path, tessdata_folder, language="eng", dpi=OCR_DPI):
    """
    Runs OCR on the full‑res screenshot and returns:
      - words: list of (text, x0, y0, x1, y1) in physical pixels
      - size: (width, height) of the screenshot in physical px
    """
    pix = fitz.Pixmap(image_path)
    if pix.n - pix.alpha >= 4:  # convert to RGB if needed
        pix = fitz.Pixmap(fitz.csRGB, pix)
    W, H = pix.width, pix.height

    # embed into one‑page PDF
    doc = fitz.open()
    page = doc.new_page(width=W, height=H)
    page.insert_image(fitz.Rect(0, 0, W, H), pixmap=pix)

    # OCR with explicit tessdata, language and DPI
    tp = page.get_textpage_ocr(
        dpi=dpi,
        full=True,
        tessdata=tessdata_folder,
        language=language
    )
    raw = page.get_text("words", textpage=tp, sort=True)
    doc.close()

    # normalize to (text, x0, y0, x1, y1)
    words = [(w[4], w[0], w[1], w[2], w[3]) for w in raw]
    return words, (W, H)

def click_word(target, words_logical):
    """
    Finds and clicks the first word containing 'target' in logical coords.
    """
    targ = target.lower()
    for text, x0, y0, x1, y1 in words_logical:
        if targ in text.lower():
            cx = x0 + (x1 - x0) / 2
            cy = y0 + (y1 - y0) / 2
            pyautogui.moveTo(cx, cy, duration=0.2)
            pyautogui.click()
            print(f"✅ Clicked ‘{text}’ at ({cx:.0f}, {cy:.0f})")
            return True
    print(f"❌ No element matching “{target}” found.")
    return False

def main():
    # 1) detect DPI scaling
    scale = get_windows_scaling()
    print(f"ℹ️  Detected Windows scaling: {scale:.2f}×")

    # 2) screenshot at full physical resolution
    pyautogui.screenshot(SCREENSHOT_PATH)
    print(f"🖼  Screenshot saved: {SCREENSHOT_PATH}")

    # 3) OCR → get physical‑px boxes
    print("🔎 Running OCR…")
    words_phys, (W, H) = extract_words_physical(SCREENSHOT_PATH, TESSDATA_FOLDER)
    print(f"🔤 OCR found {len(words_phys)} words at {W}×{H} px")

    # 4) convert to logical coords for clicking
    words_logical = [
        (txt, x0/scale, y0/scale, x1/scale, y1/scale)
        for (txt, x0, y0, x1, y1) in words_phys
    ]
    # (optionally) sort by y,x if you want consistent matching order:
    words_logical.sort(key=lambda e: (e[2], e[1]))

    # 5) interactive click loop
    print("\nType text to click (e.g. ‘Selection’ or ‘1.py’), or ‘exit’ to quit.")
    while True:
        target = input("Element to click: ").strip()
        if target.lower() in ("exit", "quit"):
            break
        click_word(target, words_logical)
        time.sleep(0.2)

if __name__ == "__main__":
    if not os.path.isdir(TESSDATA_FOLDER):
        raise RuntimeError(f"Tessdata folder not found: {TESSDATA_FOLDER}")
    main()
