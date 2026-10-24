import re
import tkinter as tk
from datetime import datetime
import requests
import speech_recognition as sr
import threading
import subprocess
from tkinter import scrolledtext


def get_assistant_response(message: str) -> str:
    try:
        response = requests.post(
            "http://localhost:4891/v1/chat/completions",
            json={
                "model": "Llama 3.2 1B Instruct",
                "messages": [{"role": "user", "content": message}],
                "temperature": 0.7,
                "max_tokens": 300
            },
            timeout=120
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return "AI connection error: " + str(e)


def main() -> None:
    root = tk.Tk()
    root.title("JARVIS AI Assistant")
    root.geometry("900x700+100+50")
    root.configure(bg="#07111f")

    title = tk.Label(
        root,
        text="J.A.R.V.I.S",
        font=("Arial", 28, "bold"),
        fg="#00d9ff",
        bg="#07111f",
    )
    title.pack(pady=20)

    status = tk.Label(
        root,
        text="AI ASSISTANT READY",
        font=("Arial", 12),
        fg="#00ff99",
        bg="#07111f",
    )
    status.pack()

    chat = scrolledtext.ScrolledText(
        root,
        bg="#101f30",
        fg="white",
        font=("Arial", 12),
        insertbackground="white",
        wrap=tk.WORD,
        state=tk.DISABLED,
    )
    chat.pack(padx=20, pady=20, fill="both", expand=True)

    def add_chat_line(sender: str, message: str) -> None:
        chat.configure(state=tk.NORMAL)
        chat.insert(tk.END, f"{sender}: {message}\n\n")
        chat.configure(state=tk.DISABLED)
        chat.see(tk.END)

    add_chat_line(
        "JARVIS",
        "Hello! Welcome to your AI assistant. Type 'help' to get started.",
    )

    entry = tk.Entry(
        root,
        font=("Arial", 14),
        bg="#182b40",
        fg="white",
        insertbackground="white",
    )
    entry.pack(padx=20, pady=5, fill="x")

    pending_delete = {"term": ""}

    def send_message() -> None:
        message = entry.get().strip()
        if not message:
            return

        add_chat_line("YOU", message)
        low = message.lower()
        if "save a note" in low:
            note = re.split("save a note", message, flags=re.I, maxsplit=1)[1].strip(" :")
            if not note:
                answer = "Please say save a note, then your note."
            else:
                try:
                    from google.oauth2.credentials import Credentials
                    from googleapiclient.discovery import build
                    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/spreadsheets"])
                    service = build("sheets", "v4", credentials=creds)
                    service.spreadsheets().values().append(spreadsheetId="1xskwsBZWOFNGSOYSxfTiafnhVj9V1x7yCZ92bWC8UrY", range="Sheet1!A:B", valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body={"values": [[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), note]]}).execute()
                    answer = "I saved your note to Google Sheets: " + note
                except Exception as error:
                    answer = "Could not save note: " + str(error)
        elif "delete my" in low and "note" in low:
            term = re.sub(r"(?i)delete my|notes?", "", message).strip(" :").lower()
            if term:
                pending_delete["term"] = term
                answer = "To confirm, say: confirm delete note " + term
            else:
                answer = "Please say the note name."
        elif "confirm delete note" in low:
            term = re.sub(r"[^a-z0-9 ]", "", message.lower().split("confirm delete note", 1)[1]).strip()
            expected = pending_delete["term"]
            if expected and term == expected:
                try:
                    from google.oauth2.credentials import Credentials
                    from googleapiclient.discovery import build
                    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/spreadsheets"])
                    service = build("sheets", "v4", credentials=creds)
                    sid = "1xskwsBZWOFNGSOYSxfTiafnhVj9V1x7yCZ92bWC8UrY"
                    result = service.spreadsheets().values().get(spreadsheetId=sid, range="Sheet1!A:B").execute()
                    rows = result.get("values", [])
                    index = next((i for i, row in enumerate(rows) if i > 0 and len(row) > 1 and re.match(r"^\d{4}-\d{2}-\d{2}", row[0]) and expected in row[1].lower()), None)
                    if index is not None:
                        service.spreadsheets().batchUpdate(spreadsheetId=sid, body={"requests": [{"deleteDimension": {"range": {"sheetId": 0, "dimension": "ROWS", "startIndex": index, "endIndex": index + 1}}}]}).execute()
                        answer = "Deleted your note: " + expected
                    else:
                        answer = "I could not find that note. Nothing was deleted."
                except Exception as error:
                    answer = "Could not delete note: " + str(error)
                pending_delete["term"] = ""
            else:
                answer = "Confirmation did not match. Nothing was deleted. Please repeat the full confirmation."
        elif "find my" in low and "note" in low:
            term = re.sub(r"(?i)find my|note", "", message).strip(" :")
            query = term.lower()
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/spreadsheets"])
                service = build("sheets", "v4", credentials=creds)
                result = service.spreadsheets().values().get(spreadsheetId="1xskwsBZWOFNGSOYSxfTiafnhVj9V1x7yCZ92bWC8UrY", range="Sheet1!A:B").execute()
                rows = result.get("values", [])
                matches = [row[1] for row in rows if len(row) > 1 and query in row[1].lower()]
                if matches:
                    answer = "I found your note. " + ". ".join(matches[-10:])
                else:
                    answer = "I could not find a note matching " + term
            except Exception as error:
                answer = "Could not search notes: " + str(error)
        elif "read my notes" in low:
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build
                creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/spreadsheets"])
                service = build("sheets", "v4", credentials=creds)
                result = service.spreadsheets().values().get(spreadsheetId="1xskwsBZWOFNGSOYSxfTiafnhVj9V1x7yCZ92bWC8UrY", range="Sheet1!A:B").execute()
                rows = result.get("values", [])
                notes = [row[1] for row in rows if len(row) > 1 and re.match(r"^\d{4}-\d{2}-\d{2}", row[0])]
                if notes:
                    answer = "Here are your saved notes. " + ". ".join(notes[-10:])
                else:
                    answer = "You have no saved notes yet."
            except Exception as error:
                answer = "Could not read notes: " + str(error)
        elif "open google" in low:
            subprocess.Popen(["open", "https://www.google.com"])
            answer = "Opening Google."
        elif "open youtube" in low:
            subprocess.Popen(["open", "https://www.youtube.com"])
            answer = "Opening YouTube."
        elif "open safari" in low:
            subprocess.Popen(["open", "-a", "Safari"])
            answer = "Opening Safari."
        elif "what time is it" in low or low == "time":
            answer = "The time is " + datetime.now().strftime("%I:%M %p")
        else:
            answer = get_assistant_response(message)
        add_chat_line("JARVIS", answer)
        threading.Thread(target=lambda: subprocess.run(["say", "-v", "Alex", "-r", "230", answer]), daemon=True).start()
        entry.delete(0, tk.END)
        entry.focus_set()

    button = tk.Button(
        root,
        text="SEND",
        command=send_message,
        bg="#00aacc",
        fg="white",
        font=("Arial", 12, "bold"),
    )
    button.pack(pady=12)

    voice_language = {"value": "en-IN"}

    def set_voice_language(language):
        voice_language["value"] = language
        label = "Hindi" if language == "hi-IN" else "English"
        add_chat_line("JARVIS", "Voice language set to " + label)

    def listen_voice():
        def worker():
            try:
                r = sr.Recognizer()
                with sr.Microphone(device_index=0) as source:
                    root.after(0, lambda: add_chat_line("JARVIS", "Listening... Speak now."))
                    audio = r.listen(source, timeout=8, phrase_time_limit=10)
                message = r.recognize_google(audio, language=voice_language["value"])
                def process():
                    entry.delete(0, tk.END)
                    entry.insert(0, message)
                    send_message()
                root.after(0, process)
            except Exception as e:
                root.after(0, lambda error=str(e): add_chat_line("JARVIS", "Voice error: " + error))
        threading.Thread(target=worker, daemon=True).start()

    listen_button = tk.Button(root, text="LISTEN", command=listen_voice, bg="#007788", fg="white", font=("Arial", 12, "bold"))
    listen_button.pack(pady=5)
    language_frame = tk.Frame(root)
    language_frame.pack(pady=4)
    tk.Button(language_frame, text="English", command=lambda: set_voice_language("en-IN")).pack(side="left", padx=5)
    tk.Button(language_frame, text="Hindi", command=lambda: set_voice_language("hi-IN")).pack(side="left", padx=5)

    entry.bind("<Return>", lambda _event: send_message())
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
