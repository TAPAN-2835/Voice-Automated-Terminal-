import subprocess
import pyttsx3
import os
import platform
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import tempfile
import cv2
import mediapipe as mp
import time

# ---------- Setup ----------
engine = pyttsx3.init()

def speak(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()

# ---------- Detect OS ----------
current_os = platform.system()
print(f"Detected OS: {current_os}")

# ---------- Command Map ----------
def get_command_map():
    if current_os == "Windows":
        return {
            "list files": "dir",
            "list directory": "dir",
            "current directory": "cd",
            "make folder": "mkdir test_folder",
            "change directory": "cd ..",
            "go to desktop": "cd %userprofile%\\Desktop",
            "go to downloads": "cd %userprofile%\\Downloads",
            "delete folder": "rmdir /s /q test_folder",
            "rename file": "rename test.txt renamed_test.txt",
            "clear screen": "cls",
            "system info": "systeminfo",
            "show date": "date /t",
            "show time": "time /t",
            "show processes": "tasklist",
            "show cpu usage": "wmic cpu get loadpercentage",
            "show memory usage": "wmic OS get FreePhysicalMemory,TotalVisibleMemorySize /Format:List",
            "disk usage": "wmic logicaldisk get size,freespace,caption",
            "network info": "ipconfig /all",
            "ping google": "ping google.com",
            "show ip": "ipconfig | findstr IPv4",
            "open browser": "start https://www.google.com"
        }
    else:
        return {
            "list files": "ls -la",
            "list directory": "ls -la",
            "current directory": "pwd",
            "make folder": "mkdir test_folder",
            "change directory": "cd ..",
            "go to desktop": "cd ~/Desktop",
            "go to downloads": "cd ~/Downloads",
            "delete folder": "rm -rf test_folder",
            "rename file": "mv test.txt renamed_test.txt",
            "clear screen": "clear",
            "system info": "uname -a",
            "show date": "date",
            "show time": "date +%T",
            "show processes": "ps aux --sort=-%mem | head",
            "show cpu usage": "top -bn1 | grep 'Cpu(s)'",
            "show memory usage": "free -h",
            "disk usage": "df -h",
            "network info": "ifconfig",
            "ping google": "ping -c 3 google.com",
            "show ip": "hostname -I",
            "open browser": "xdg-open https://www.google.com" if current_os == "Linux" else "open https://www.google.com"
        }

command_map = get_command_map()

# ---------- Gesture Command Mapping ----------
gesture_command_map = {
    0: "clear screen",
    1: "system info",
    2: "show processes",
    3: "show cpu usage",
    4: "show memory usage",
    5: "disk usage",
    6: "network info",
    7: "ping google",
    8: "show ip",
    9: "open browser"
}

# ---------- Fuzzy / Synonym Matching ----------
def find_best_match(user_input):
    user_input = user_input.lower()
    for key in command_map:
        if key in user_input:
            return key, command_map[key]
    synonyms = {
        "show": ["display", "get", "print"],
        "list": ["show", "display"],
        "delete": ["remove", "erase"],
        "create": ["make", "new"],
        "open": ["launch", "start"],
        "check": ["see", "view", "verify"],
    }
    for key in command_map:
        for word in key.split():
            for syn_key, syn_list in synonyms.items():
                if word == syn_key and any(syn in user_input for syn in syn_list):
                    return key, command_map[key]
    return None, None

# ---------- Execute Command ----------
def execute_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            print(output)
            speak("Command executed.")
        else:
            speak("Command executed successfully.")
    except subprocess.TimeoutExpired:
        speak("Command timed out.")
    except Exception as e:
        print(f"Error: {e}")
        speak("Command failed.")

# ---------- Audio Input ----------
def record_audio(duration=5):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            filename = f.name
        print(f"Recording for {duration} seconds...")
        data = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
        sd.wait()
        sf.write(filename, data, 44100)
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio).lower()
        return text
    except Exception as e:
        print(f"Voice input failed: {e}")
        speak("Voice input failed. Please type your command.")
        return input("Type your command: ").lower()

# ---------- Gesture Recognition (Two Hands) ----------
def gesture_control():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=2)
    mp_draw = mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    prev_command = None
    last_exec_time = 0

    speak("Gesture control activated. Show one or both hands to execute commands.")
    print("Press 'q' to quit gesture mode.")

    while True:
        success, img = cap.read()
        if not success:
            speak("Camera not detected.")
            break

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
                finger_tips = [4, 8, 12, 16, 20]
                landmarks = handLms.landmark
                finger_count = 0
                if landmarks[finger_tips[0]].x < landmarks[finger_tips[0] - 1].x:
                    finger_count += 1
                for tip in finger_tips[1:]:
                    if landmarks[tip].y < landmarks[tip - 2].y:
                        finger_count += 1

                cv2.putText(img, f"Fingers: {finger_count}", (20, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                if time.time() - last_exec_time > 3:
                    if finger_count in gesture_command_map:
                        command_name = gesture_command_map[finger_count]
                        if command_name != prev_command:
                            speak(f"Executing: {command_name}")
                            execute_command(command_map[command_name])
                            prev_command = command_name
                            last_exec_time = time.time()

        cv2.imshow("Gesture Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            speak("Exiting gesture control.")
            break

    cap.release()
    cv2.destroyAllWindows()

# ---------- Mode Selection ----------
def select_mode():
    print("Select control mode:")
    print("1. Text")
    print("2. Audio (Voice)")
    print("3. Gesture (Hand)")
    return input("Enter your choice (1/2/3): ").strip()

# ---------- Main ----------
if _name_ == "_main_":
    mode = select_mode()

    if mode == "1":
        speak("Text control activated.")
        while True:
            command_text = input("Type your command: ").lower()
            if command_text in ["exit", "quit", "stop"]:
                speak("Goodbye.")
                break
            key, cmd = find_best_match(command_text)
            if cmd:
                execute_command(cmd)
            else:
                speak("No matching command found.")

    elif mode == "2":
        speak(f"Voice shell activated on {current_os}. Say a command or 'exit' to quit.")
        while True:
            command_text = record_audio()
            print(f"You said: '{command_text}'")
            if any(word in command_text for word in ["exit", "quit", "stop", "goodbye"]):
                speak("Exiting voice shell. Goodbye.")
                break
            key, cmd = find_best_match(command_text)
            if cmd:
                execute_command(cmd)
            else:
                speak("No matching command found.")

    elif mode == "3":
        gesture_control()

    else:
        speak("Invalid choice. Exiting.")
