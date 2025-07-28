import pyautogui
import time

# Perform actions based on user input
def perform_action(user_input):
    app = user_input.strip().lower()
    if app:
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write(app)
        time.sleep(0.5)
        pyautogui.press("enter")
        return f"Opened: {app}"
    return "⚠️ No input provided."

# Main Chat Loop
def chat():
    print("💻 Simple App Opener ready. Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Bye.")
            break

        result = perform_action(user_input)
        print(f"🔧 {result}")

if __name__ == "__main__":
    chat()
