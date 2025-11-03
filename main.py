import subprocess
import pyttsx3
import os
import platform
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import tempfile

# ---------- Setup ----------
engine = pyttsx3.init()

def speak(text):
    print("💬", text)
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()

# ---------- Detect OS ----------
current_os = platform.system()
print(f"🖥  Detected OS: {current_os}")

# ---------- Cross-platform command map ----------
def get_command_map():
    if current_os == "Windows":
        return {
            "list files": "dir",
            "list directory": "dir",
            "current directory": "cd",
            "make folder": "mkdir test_folder",
            "clear screen": "cls",
            "show processes": "tasklist",
            "system info": "systeminfo",
            "open notepad": "notepad",
            "network info": "ipconfig",
            "disk usage": "wmic logicaldisk get size,freespace,caption",
            "create test file": "echo Hello from voice shell! > test.txt",
            "read test file": "type test.txt",
            "delete test file": "del test.txt",
            "copy test file": "copy test.txt test_copy.txt",
            "show date": "date /t",
            "show time": "time /t",
        }
    else:  # Linux/Mac
        return {
            "list files": "ls -la",
            "list directory": "ls -la",
            "current directory": "pwd",
            "make folder": "mkdir test_folder",
            "clear screen": "clear",
            "show processes": "ps aux",
            "system info": "uname -a",
            "open editor": "nano" if current_os == "Linux" else "open -a TextEdit",
            "network info": "ifconfig" if current_os == "Linux" else "ifconfig",
            "disk usage": "df -h",
            "create test file": "echo 'Hello from voice shell!' > test.txt",
            "read test file": "cat test.txt",
            "delete test file": "rm test.txt",
            "copy test file": "cp test.txt test_copy.txt",
            "show date": "date",
            "show time": "date +%T",
            "free memory": "free -h" if current_os == "Linux" else "vm_stat",
        }

command_map = get_command_map()

# ---------- Natural Language Processing ----------
def find_best_match(user_input):
    """Find best matching command using fuzzy matching"""
    user_input = user_input.lower()
    
    # Direct match
    for key in command_map:
        if key in user_input:
            return key, command_map[key]
    
    # Synonym matching
    synonyms = {
        "show": ["display", "get", "print"],
        "list": ["show", "display"],
        "delete": ["remove", "erase"],
        "create": ["make", "new"],
    }
    
    for key in command_map:
        for word in key.split():
            for syn_key, syn_list in synonyms.items():
                if word == syn_key and any(syn in user_input for syn in syn_list):
                    return key, command_map[key]
    
    return None, None

# ---------- Execute command safely ----------
def execute_command(cmd):
    try:
        if current_os == "Windows":
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        else:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10, executable='/bin/bash')
        
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            print(output)
            first_line = output.split('\n')[0]
            speak(f"Command executed. {first_line[:50]}")
        else:
            speak("Command executed successfully.")
    except subprocess.TimeoutExpired:
        speak("Command timed out.")
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("Command failed.")

# ---------- Help system ----------
def show_help():
    print("\n📋 Available commands:")
    for i, key in enumerate(command_map.keys(), 1):
        print(f"  {i}. {key}")
    speak(f"There are {len(command_map)} available commands. Check the console.")

# ---------- Record audio function ----------
def record_audio(duration=5):
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            filename = f.name
        print(f"🎤 Recording for {duration} seconds...")
        data = sd.rec(int(duration * 44100), samplerate=44100, channels=1)
        sd.wait()
        sf.write(filename, data, 44100)
        with sr.AudioFile(filename) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio).lower()
        return text
    except Exception as e:
        print(f"⚠ Voice input failed: {e}")
        speak("Voice input failed. Please type your command.")
        return input("Type your command: ").lower()

# ---------- Main Loop ----------
speak(f"Voice shell activated on {current_os}. Say a command or type 'help'.")

while True:
    try:
        command_text = record_audio()

        print(f"👉 You said: '{command_text}'")

        # Exit commands
        if any(word in command_text for word in ["exit", "quit", "stop", "goodbye"]):
            speak("Exiting voice shell. Goodbye.")
            break

        # Help command
        if "help" in command_text or "commands" in command_text:
            show_help()
            continue

        # Find and execute command
        key, cmd = find_best_match(command_text)
        if cmd:
            speak(f"Executing: {key}")
            execute_command(cmd)
        else:
            speak("No matching command found. Say help for available commands.")

    except KeyboardInterrupt:
        speak("Interrupted. Exiting.")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
        speak("Something went wrong.")