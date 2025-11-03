🗣️ Voice Command Shell

A cross-platform voice-controlled command shell that lets you execute system commands using speech recognition.
It supports both Windows and Linux/Mac, automatically detecting the operating system and mapping your natural voice commands to shell commands.

🚀 Features

🎙️ Voice Command Execution: Control your system using spoken commands.

🧠 Cross-Platform Support: Works on both Windows and Linux/macOS.

🗺️ Command Mapping: Maps natural language commands to real shell commands.

💬 Text-to-Speech Feedback: Uses pyttsx3 to provide spoken feedback after each command.

🔍 Natural Language Matching: Basic fuzzy and synonym matching for flexible input.

🧾 Command Help Menu: Lists all supported commands on request.

⚙️ Safe Command Execution: Runs commands in a controlled subprocess environment with timeouts.

🏗️ Project Structure
voice_command_shell/
│
├── main.py               # Main Python file (your provided code)
├── README.md             # Project documentation
└── requirements.txt      # Dependencies (optional but recommended)

⚙️ Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/voice-command-shell.git
cd voice-command-shell

2️⃣ Install Dependencies

Make sure you have Python 3.8+ installed, then install the required packages:

pip install pyttsx3 SpeechRecognition sounddevice soundfile


For some systems, you may also need:

pip install pyaudio  # for microphone access (Windows)
sudo apt install portaudio19-dev python3-pyaudio  # Linux

▶️ Usage
1️⃣ Run the Script
python main.py

2️⃣ Speak Your Commands

After activation, say commands like:

Example Voice Command	What It Does
“List files”	Shows all files in current directory
“Make folder”	Creates a folder named test_folder
“System info”	Displays system information
“Network info”	Shows network configuration
“Create test file”	Creates a file named test.txt
“Read test file”	Displays contents of test.txt
“Delete test file”	Deletes the test file
“Show date”	Displays current date
“Show time”	Displays current time

Say “help” anytime to list all available commands.

🎧 How Voice Input Works

The program records audio using the sounddevice library.

It saves the audio temporarily using soundfile.

The speech_recognition library converts your voice into text.

The recognized command is matched against predefined keywords.

A system command is executed using subprocess, and output is spoken via pyttsx3.

🧠 Tech Stack
Component	Library Used
Speech Recognition	speech_recognition
Audio Recording	sounddevice
Audio File Handling	soundfile
Text-to-Speech	pyttsx3
OS Interaction	subprocess, platform, os
Temporary File Handling	tempfile
🛡️ Safety

Commands are executed with timeouts (10 seconds max).

The script uses read-only or safe operations by default.

You can modify the command_map dictionary to add your own commands.

🧩 Adding Custom Commands

To add more voice commands, edit the get_command_map() function:

"open calculator": "calc",
"show ip": "ipconfig"  # Windows


Or for Linux/Mac:

"open editor": "nano",
"show ip": "ifconfig"

🗃️ Example Output
🖥  Detected OS: Windows
💬 Voice shell activated on Windows. Say a command or type 'help'.
🎤 Recording for 5 seconds...
👉 You said: 'list files'
💬 Executing: list files
 Directory of C:\Users\Admin\Desktop
💬 Command executed. Directory of C:\Users\Admin\Desktop

🧹 Exit the Program

Say:

exit
quit
stop
goodbye


Or press Ctrl + C.