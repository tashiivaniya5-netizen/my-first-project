import pyttsx3
from gpt4all import GPT4All

model = GPT4All(
    "Llama-3.2-1B-Instruct-Q4_0.gguf",
    model_path="/Users/Tashi/Library/Application Support/nomic.ai/GPT4All"
)

print("AI is thinking...")
answer = model.generate("Say: Hello! I am Jarvis. How can I help you?", max_tokens=40)
print("AI answer:", answer)

print("Starting voice...")
engine = pyttsx3.init()
engine.setProperty("volume", 1.0)
engine.say(answer)
engine.runAndWait()
print("Voice finished.")
