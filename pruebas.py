from tkinter import *
import pandas as pd
import whisper
from whisper.utils import get_writer
from openai import OpenAI
from config import OPEN_AI_API_KEY, MODEL_VERSION,TEMPERATURE_MEMORY

#Cargamos key openai
client = OpenAI(
  api_key=OPEN_AI_API_KEY,
)

#TRANSCRIBIR
def transcribir(modo:str, path:str, ventana, ventana_texto01): 
  ventana_texto01.delete("1.0", "end")
  # Inserta el texto en la ventana de texto
  ventana_texto01.insert("1.0", "Trancribiendo...")
  # Actualiza la ventana de Tkinter
  ventana.update() 
  
  #transcripción
  model = whisper.load_model(modo) #tiny(1gb); base(1gb); small(2gb); medium(5gb); large(10gb)
  result = model.transcribe(path)

  global Transcripcion
  Transcripcion =  result
  
  # Inserta el texto en la ventana de texto
  ventana_texto01.delete("1.0", "end")
  ventana_texto01.insert("1.0", Transcripcion['text'])
  ventana.update()    

  return result


#RESUMIR
def resumir(model:str,Transcripcion, ventana, ventana_texto02, prompt_type):
  
  """ 
    Generación de reporte
    
      Args:
        Transcripcion (str): Texto de entrada dado por el transcriptor. 

      Returns:
        openai_type: reporte que se infirió a partir del texto. 
    """
    

  
  ventana_texto02.delete("1.0", "end")
  ventana_texto02.insert("1.0", "Resumiendo...")
  # Actualiza la ventana de Tkinter
  ventana.update() 
  
  if size_selector.get() == "Largo":
    texto_size = 15
  if size_selector.get() == "Medio":
    texto_size = 10
  if size_selector.get() == "Corto":
    texto_size = 5
  
  #Calculamos proporcion del resumen
  text = Transcripcion['text']
  
  words_counter = len(text.split())
  sumary_size = round((words_counter*texto_size) /100)
      
  if prompt_selector.get():
    prompt_type = prompt_selector.get()
      
  #SELECTOR DE TIPO DE PROMPT
  if prompt_type == "Academico":
    prompt = f"Your task is to synthesize a comprehensive report based on transcribed text from a university lecture. Your report should be about {sumary_size} words. Your report should distill the core subject matter, enumerate the key concepts discussed, and catalog noteworthy comments made during the session. Please proceed to construct a detailed report on the following text: {text}"
  
  if prompt_type == "Narrativo":
    prompt = f"Your task is to synthesize a comprehensive report based on transcribed text from a narrative audio. Your report should be about {sumary_size} words. It should distill the core subject matter, enumerate the key concepts discussed, and catalog noteworthy comments made during the session. Please proceed to construct a detailed report on the following text: {text}"

  if prompt_type == "Noticia":
    prompt = f"Your task is to generate a concise news summary based on the provided text from recent news articles. Your summary should be approximately {sumary_size} words. Condense the core information, highlight key events, and outline notable details discussed in the articles. Please proceed to craft an informative summary of the following news text: {text}"

  #DEFINIMOPS MENSAKE
  message = [
      {"role": "system", "content": "You are an advanced information collector and synthesizer."},
      {"role": "user", "content": prompt}] 
  
  # API Call
  try:
    sumary_response = client.chat.completions.create(
      messages=message,
      model=model,
      temperature = TEMPERATURE_MEMORY,
  )
  except Exception as e:
    print(f"Ocurrió algún error con el llamado a la API de OpenAI: {e}") 
    return ""
  
  global sumary
  sumary =  sumary_response
  
  # Inserta el texto en la ventana de texto
  ventana_texto02.delete("1.0", "end")
  ventana_texto02.insert("1.0", sumary.choices[0].message.content)
  # Actualiza la ventana de Tkinter
  ventana.update()    
  return sumary_response
  
  
#TKINTER
  
from tkinter import filedialog
from tkinter import ttk
ventana = Tk()
#ventana.geometry("500x450")

ruta = None
texto_size = ""
prompt_type = "Academico"

def openFile():
  global ruta
  ruta = filedialog.askopenfilename(initialdir="N:/MisArchivos/Universidad/4toaño/2doSemestre/PISS_/Audios")
  #filedialog.askopenfilename(initialdir=os.getcwd()) 
    
ventana_texto01 = Text(ventana)
ventana_texto01.config(width=60, height=10)

ventana_texto02 = Text(ventana)
ventana_texto02.config(width=60, height=10)

buttonOpenFile = Button(text="Selecciona tu audio",command=openFile)

buttonTranscribe = Button(text="Transcribir", command=lambda: transcribir("small", ruta,ventana, ventana_texto01))

prompt_selector = ttk.Combobox(ventana, values= ["Academico", "Narrativo", "Noticia"], width=10, height=1)

size_selector = ttk.Combobox(ventana, values=["Largo", "Medio", "Corto"], width=10, height=1)

buttonResumir = Button(text="Resumir", command=lambda: resumir(MODEL_VERSION,Transcripcion, ventana, ventana_texto02, prompt_type))

ventana_texto01.grid(row=0, column=0, columnspan=6,padx=10, pady=10)
ventana_texto02.grid(row=1, column=0, columnspan=6,padx=10, pady=10)
buttonOpenFile.grid(row=2, column=1, padx=10, pady=10)
buttonTranscribe.grid(row=2, column=2, padx=10, pady=10)
prompt_selector.grid(row=2, column=3, padx=10, pady=10)
size_selector.grid(row=2, column=4, padx=10, pady=10)
buttonResumir.grid(row=2, column=5, padx=10, pady=10)

ventana.mainloop()