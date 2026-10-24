import speech_recognition as sr
import pyttsx3
from gpt4all import GPT4All

engine = pyttsx3.init()
engine.setProperty("rate", 230)
engine.setProperty("volume", 1.0)
engine.setProperty("voice", "com.apple.speech.synthesis.voice.Alex")

def speak(text):
    import subprocess
    print("JARVIS:", text, flush=True)
    subprocess.run(["say", "-v", "Alex", "-r", "230", text])

recognizer = sr.Recognizer()
microphone = sr.Microphone(device_index=0)

model = GPT4All(
    "Llama-3.2-1B-Instruct-Q4_0.gguf",
    model_path="/Users/Tashi/Library/Application Support/nomic.ai/GPT4All",
    n_threads=4
)

speak("Hello! Jarvis is ready. Please speak.")

while True:
    try:
        with microphone as source:
            print("\nListening... Speak now.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)

        question = recognizer.recognize_google(audio)
        print("You:", question)

        if question.lower() in ["exit", "quit", "goodbye", "bye"]:
            speak("Goodbye!")
            break

        with model.chat_session():
            answer = model.generate("Reply in one short sentence: " + question, max_tokens=20, temp=0.2)

        speak(answer)

    except sr.WaitTimeoutError:
        print("I didn't hear anything. Try again.")
    except sr.UnknownValueError:
        speak("Sorry, please repeat.")
    except sr.RequestError as error:
        print("Internet or speech recognition error:", error)
        speak("Speech recognition needs internet.")
    except KeyboardInterrupt:
        print("\nJarvis stopped.")
        break
