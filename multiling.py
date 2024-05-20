import time
import openai
import speech_recognition as sr
from gtts import gTTS
import os
import pygame
from googletrans import Translator

openai.api_key = "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"

def chatbot_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=messages
    )
    message = response['choices'][0]['message']['content']
    return message

def text_to_speech(text, lang):
    if not pygame.mixer.get_init():
        pygame.mixer.init()

    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save("temp.mp3")

        pygame.mixer.music.load("temp.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(1)

        pygame.mixer.quit()
        os.remove("temp.mp3")

    except Exception as e:
        print("Error:", str(e))

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        user_input = recognizer.recognize_google(audio, language="hi-IN")
        print(f"You: {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
        return None

def run_chatbot():
    default_prompt = "Answer in details in Hinglish language:"

    # Replace the following line with your input mechanism
    user_input = recognize_speech()

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": default_prompt + "\nYou: " + user_input}
    ]

    if user_input:
        try:
            response = chatbot_response(messages)
            print(f"Chatbot: {response}")

            # Determine the language of the user's input (Hindi, Bengali, or English)
            lang = "hi"  # Default to Hindi

            if "bengali" in user_input.lower():
                lang = "bn"
            elif "english" in user_input.lower():
                lang = "en"

            # Translate the response to the specified language
            translator = Translator()
            response_in_lang = translator.translate(response, dest=lang).text
            print(f"Translated Response: {response_in_lang}")

            # Read the translated text response using gTTS and play it with pygame
            text_to_speech(response_in_lang, lang)

        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    print("Chatbot with Whisper")
    run_chatbot()
