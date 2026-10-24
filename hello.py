
import tkinter as tk
from tkinter import scrolledtext
from openai import OpenAI

client = OpenAI()

root = tk.Tk()
root.title("JARVIS AI Assistant")
root.geometry("700x500")
root.configure(bg="#07111f")

chat = scrolledtext.ScrolledText(
    root,
    bg="#101f30",
    fg="white",
    font=("Arial", 12),
    wrap=tk.WORD
)
chat.pack(padx=15, pady=15, fill="both", expand=True)
chat.insert("end", "JARVIS: Hello! Ask me anything.\n")

entry = tk.Entry(root, font=("Arial", 14))
entry.pack(padx=15, fill="x")

def send_message():
    message = entry.get().strip()
    if not message:
        return

    chat.insert("end", f"\nYOU: {message}\n")
    entry.delete(0, "end")
    root.update_idletasks()

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=message
        )
        answer = response.output_text
    except Exception as e:
        answer = f"Error: {e}"

    chat.insert("end", f"JARVIS: {answer}\n")
    chat.see("end")

button = tk.Button(root, text="SEND", command=send_message)
button.pack(pady=10)

entry.bind("<Return>", lambda event: send_message())

root.mainloop()
