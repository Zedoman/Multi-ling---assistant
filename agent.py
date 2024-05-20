import time
import openai
import speech_recognition as sr
from gtts import gTTS
import os
import pygame

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
        print(f"You (Insurance Agent): {user_input}")
        return user_input
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition request failed: {e}")
        return None

def run_chatbot():
    default_prompt = (
        "Age aur vyavsay - Salaried, 40 saal\n"
        "Parivaar ki sthiti - Shaadi shuda, 2 bacche\n"
        "Vittiya sthiti - Madhyam varg, 15 lakh varshik aay, car loan 8 lakh\n"
        "Maujooda bima suraksha 5 lakh aur 50 lakh ka group bima naukri se\n"
        "Chinta ya prathirtyein - Ghar kharidna hai aur bacchon ke bhavishya ka yojana karna hai\n"
        "Swasthya sthiti - Swasth\n"
        "Ichchhit suraksha - pata nahi\n"
        "Budget ki jagah - haan\n"
        "Nirnay lene ka tarika - sanvatpoorn\n"
        "Vittiya gyaan ka star - madhyam\n"
        "Vishwas ki samasya - anjaane logon par jaldi bharosa nahi karta"
    )

    print("Insurance Assistant Chatbot")
    print("Aap vyakti ke vivaran ke baare mein prashna kar sakte hain. Prerit hone ke liye 'exit' type karein.")

    while True:
        # Replace the following line with your input mechanism
        user_input = recognize_speech()

        if user_input.lower() == 'exit':
            print("Conversation samapt ho rahi hai.")
            break

        # Adjusting the role from "user" to "assistant" for AI responses
        messages = [
            {"role": "system", "content": "Tum ek AI-shaktishaali bima sahayak ho."},
            {"role": "assistant", "content": default_prompt},
            {"role": "user", "content": user_input}
        ]

        try:
            response = chatbot_response(messages)
            print(f"AI (User): {response}")

            # Modify the response to consistently use "Meri"
            response = response.replace("आपकी", "मेरी")

            # Read the text response using gTTS and play it with pygame
            text_to_speech(response, "hi")

        except Exception as e:
            print("Error:", str(e))

if __name__ == "__main__":
    run_chatbot()
