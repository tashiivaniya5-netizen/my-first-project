import re
import tkinter as tk
from datetime import datetime
import requests
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

    def send_message() -> None:
        message = entry.get().strip()
        if not message:
            return

        add_chat_line("YOU", message)
        add_chat_line("JARVIS", get_assistant_response(message))
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

    entry.bind("<Return>", lambda _event: send_message())
    entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
