import google.generativeai as genai
import speech_recognition as sr
from datetime import date
from gtts import gTTS
from io import BytesIO
from pygame import mixer 
import threading
import queue
import os
import time

mixer.init()
mixer.set_num_channels(1)
voice = mixer.Channel(0)

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# Set Google Gemini API key
genai.configure(api_key="AIzaSyAXftwz7yaZwht6Uw8Gg0wh8fKSgUdDR0Q")

# Initialize Google Gemini API model
model = genai.GenerativeModel('gemini-pro',
    generation_config=genai.GenerationConfig(
        candidate_count=1,
        top_p=0.7,
        top_k=4,
        max_output_tokens=120,
        temperature=0.7,
    ))

chat = model.start_chat(history=[])
today = str(date.today())

# Initialize counters  
numtext = 0 
numtts = 0 
numaudio = 0

def speak_text(text):
    global slang
    
    if slang == "en-US":
        tklang = "en"
    elif slang == "hi-IN":
        tklang = "hi"
    elif slang == "bn-IN":
        tklang = 'bn'
        
    mp3file1 = BytesIO()
    tts = gTTS(text, lang=tklang, tld='us') 
    tts.write_to_fp(mp3file1)

    mp3file1.seek(0)
    sound1  = mixer.Sound(mp3file1)

    voice.play(sound1)
    
    while voice.get_busy():
        time.sleep(0.01)


# Thread 1: Chat Function
def chatfun(request, text_queue, llm_done):
    global numtext, chat
    
    response = chat.send_message(request, stream=True)
    
    for chunk in response:
        if chunk.candidates[0].content.parts:
            print(chunk.candidates[0].content.parts[0].text, end='') 
            text_queue.put(chunk.text.replace("*", ""))
            time.sleep(0.2)
            numtext += 1  
            
    append2log(f"AI: {response.candidates[0].content.parts[0].text} \n")
    
    llm_done.set()  # Signal completion after the loop

# Thread 2: Text to Speech
def text2speech(text_queue, tts_done, llm_done, audio_queue, stop_event):
    global numtext, numtts, slang
    
    numshort = 0
 
    if slang == "en-US":
        tklang = "en"
    elif slang == "hi-IN":
        tklang = "hi"
    else:
        tklang = 'bn'
        
    time.sleep(1.0)  
    
    while not stop_event.is_set():
        if not text_queue.empty():
            text = text_queue.get(timeout=0.5)
             
            if len(text) > 1:
                mp3file1 = BytesIO()
                tts = gTTS(text, lang=tklang, tld='us') 
                tts.write_to_fp(mp3file1)
        
                audio_queue.put(mp3file1)
                numtts += 1  
                text_queue.task_done()
            else:
                print("Skipping text: ", text)
                numshort += 1 
                text_queue.task_done()
 
        if llm_done.is_set() and numtts + numshort == numtext:
            time.sleep(0.2) 
            tts_done.set()
            mp3file1 = None
            break 

# Thread 3: Audio Playback
def play_audio(audio_queue, tts_done, stop_event):
    global numtts, numaudio 
        
    while not stop_event.is_set():
        mp3audio1 = BytesIO() 
        mp3audio1 = audio_queue.get()  

        mp3audio1.seek(0)  
        sound1  = mixer.Sound(mp3audio1) 
 
        voice.play(sound1)
 
        numaudio += 1   
 
        audio_queue.task_done() 
        
        while voice.get_busy():
            time.sleep(0.01)
        
        if tts_done.is_set() and numtts == numaudio:
            mp3audio1 = None
            break  

# Save conversation to a log file
def append2log(text):
    global today
    fname = 'chatlog-' + today + '.txt'
    with open(fname, "a", encoding='utf-8') as f:
        f.write(text + "\n")
        f.close()
      
# Define default language to work with the AI model
slang = "en-US"

# Main function
def main():
    global today, slang, chat, model, numtext, numtts, numaudio, messages
    
    rec = sr.Recognizer()
    mic = sr.Microphone()
    rec.dynamic_energy_threshold = True
    rec.energy_threshold = 300    

    sleeping = True 
    while True:     
        with mic as source:            
            rec.adjust_for_ambient_noise(source)

            print("Listening ...")
            audio = rec.listen(source)
            try: 
                text = rec.recognize_google(audio, language=slang)
 
                if sleeping:
                    if "jack" in text.lower() and slang == "en-US":
                        request = text.lower().split("jack")[1]
                        sleeping = False
                        chat = model.start_chat(history=[])

                        append2log(f"_"*40)                    
                        today = str(date.today())  
                        messages = []                      
                     
                        if len(request) < 2:
                            speak_text("Hi, there, how can I help?")
                            append2log(f"AI: Hi, there, how can I help? \n")
                            continue                      
                        elif "speak hindi with you" in request.lower():
                            slang = "hi-IN"
                            print("Now speak Hindi ...")
                            
                        elif "ask you something in hindi" in request.lower():
                            slang = "hi-IN"
                            print("Now speak Hindi ...")
                        
                        elif "speak bengali with you" in request.lower():
                            slang = "bn-IN"
                            print("Now speak Bengali ...")
                            
                        elif "ask you something in bengali" in request.lower():
                            slang = "bn-IN"
                            print("Now speak Bengali ...")
                        
                    elif "जैक" in text and slang == "hi-IN":
                        request = text[2:]  
                        sleeping = False
                        chat = model.start_chat(history=[])
                        append2log(f"_"*40)                     
                        today = str(date.today()) 
                        messages = []  
                        
                        if len(request) < 2:
                            speak_text("नमस्ते, मैं आपकी किस प्रकार सहायता कर सकता हूँ?")
                            append2log(f"AI: नमस्ते, मैं आपकी किस प्रकार सहायता कर सकता हूँ? \n")
                            continue   
                        
                        if "english with you" in request: 
                            slang = "en-US"
                            print("Now speak English ...")
                        
                    elif "জ্যাক" in text and slang == "bn-IN":
                        request = text[2:]  
                        sleeping = False
                        chat = model.start_chat(history=[])
                        append2log(f"_"*40)                     
                        today = str(date.today()) 
                        messages = []  
                        
                        if len(request) < 2:
                            speak_text("হ্যালো, আমি কিভাবে সাহায্য করতে পারি?")
                            append2log(f"AI: হ্যালো, আমি কিভাবে সাহায্য করতে পারি? \n")
                            continue   
                        
                        if "english with you" in request:
                            slang = "en-US"
                            print("Now speak English ...")
                        
                    else:
                        continue
                      
                else: 
                    request = text.lower()

                    if "that's all" in request:
                        append2log(f"You: {request}\n")
                        
                        speak_text("Bye now")
                        append2log(f"AI: Bye now. \n")                        
                        sleeping = True
                        continue
                    
                    if "jack" in request:
                        request = request.split("jack")[1]
                        
                    if "speak with you in hindi" in request.lower():
                        slang = "hi-IN"
                        print("Now speak Hindi ...")
                        
                    if "ask you something in hindi" in request.lower():
                        slang = "hi-IN"
                        print("Now speak Hindi ...")
                        
                    if "speak with you in bengali" in request.lower():
                        slang = "bn-IN"
                        print("Now speak Bengali ...")
                        
                    if "ask you something in bengali" in request.lower():
                        slang = "bn-IN"
                        print("Now speak Bengali ...")
                        
                append2log(f"You: {request}\n ")

                print(f"You: {request}\n AI: ", end='')
                
                numtext = 0 
                numtts = 0 
                numaudio = 0
                
                text_queue = queue.Queue()
                audio_queue = queue.Queue()
                
                llm_done = threading.Event()                
                tts_done = threading.Event() 
                stop_event = threading.Event()                
     
                llm_thread = threading.Thread(target=chatfun, args=(request, text_queue, llm_done,))
                tts_thread = threading.Thread(target=text2speech, args=(text_queue, tts_done, llm_done, audio_queue, stop_event,))
                play_thread = threading.Thread(target=play_audio, args=(audio_queue, tts_done, stop_event,))
 
                llm_thread.start()
                tts_thread.start()
                play_thread.start()
 
                while True:
                    if llm_done.is_set() and tts_done.is_set():
                        break  
                    time.sleep(0.05) 
 
                stop_event.set()               
                llm_thread.join()
                tts_thread.join()  
                play_thread.join()  
 
            except sr.UnknownValueError:
                speak_text("Sorry, I could not understand what you said. Please try again.")
            except sr.RequestError as e:
                speak_text("Error with speech recognition service; {0}".format(e))

if __name__ == '__main__':
    main()
