from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import os
from PIL import ImageTk, Image
import whisper
from whisper.utils import get_writer
from openai import OpenAI
from config import OPEN_AI_API_KEY, MODEL_VERSION,TEMPERATURE_MEMORY
from metod import openai_open, transcribir, resumir, openFile, speech, keywords
from playsound import playsound

#==============================================================================================================================
#Cargamos key openai
client = OpenAI(
api_key=OPEN_AI_API_KEY,
)

#==============================================================================================================================
#FUNCIONES

#TRANSCRIBIR
def transcribir(modo:str, path:str, ventana, ventana_texto01):
  
  text_name = os.path.basename(path).replace(".wav", "").replace(".mp3", "").replace(".ogg", "").replace(".flac", "").replace(".m4a", "").replace(".mpeg", "").replace(".mpga", "").replace(".webm", "").replace(".mp4", "")
  
  ventana_texto01.delete("1.0", "end")
  # Inserta el texto en la ventana de texto
  ventana_texto01.insert("1.0", "Transcribiendo...")
  # Actualiza la ventana de Tkinter
  ventana.update() 
  
  #transcripción

  model = whisper.load_model(modo) #tiny(1gb); base(1gb); small(2gb); medium(5gb); large(10gb)
  result = model.transcribe(path)

  global Transcripcion
  Transcripcion =  result
  
  global sumary_name
  sumary_name = text_name + "_summary"
  
  ruta_transcripcion = os.getcwd() + "/transcription_text/" 

  
  with open(ruta_transcripcion + str(text_name) + ".txt", "w") as archivo:
    archivo.write(Transcripcion['text'])
  
  # Inserta el texto en la ventana de texto
  ventana_texto01.delete("1.0", "end")
  ventana_texto01.insert("1.0", Transcripcion['text'])
  ventana.update()    

  return result

#RESUMIR
def resumir(model:str,Transcripcion, ventana, ventana_texto02, prompt_type, key_word:list):
  
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

  #Seleccionamos tamanho del resumen
  if size_selector.get() == "Largo (25%)":
    texto_size = 0.25
  if size_selector.get() == "Medio (15%)":
    texto_size = 0.15
  if size_selector.get() == "Corto (10%)":
    texto_size = 0.10
  
  text = Transcripcion['text']
  
  words_counter = len(text.split())
  minwords = round((texto_size - 0.03)*words_counter)
  maxwords = round((texto_size + 0.03)*words_counter)      
  
  #Palabras claves
  keyword = ""
  for key in key_word:
    keyword = keyword + str(key) + ", "
  
  print(keyword)
  
  if prompt_selector.get():
    prompt_type = prompt_selector.get()
      
  #SELECTOR DE TIPO DE PROMPT
  if prompt_type == "Academico":
    prompt =f"Your task is to synthesize a comprehensive report based on transcribed text from a university lecture. Your report should distill the core subject matter, enumerate the key concepts discussed, and catalog noteworthy comments made during the session. Focus the report with the following keywords: {keyword}. In more than {minwords} and less than {maxwords} words, please proceed to construct a detailed report on the following text: {text}."

  if prompt_type == "Narrativo":
    prompt = f"Your task is to synthesize a comprehensive report based on transcribed text from a narrative audio. This report should have a brief summary of the narrative as an introduction and a chronologically ordered list of the main events. Focus the report with the following keywords: {keyword}. In more than {minwords} and less than {maxwords} words, please proceed to construct a detailed report on the following text: {text}"

  
  #DEFINIMOPS MENSAJE
  message = [
      {"role": "system", "content": "You are an advanced information collector and synthesizer, and you only answer in Spanish."},
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
  
  ruta_sumary = os.getcwd() + "/sumary_text/" 
  
  with open(ruta_sumary + str(sumary_name) + ".txt", "w") as archivo:
    archivo.write(sumary.choices[0].message.content)
    
  # Inserta el texto en la ventana de texto
  ventana_texto02.delete("1.0", "end")
  ventana_texto02.insert("1.0", sumary.choices[0].message.content)
  # Actualiza la ventana de Tkinter
  ventana.update()    
  return sumary_response
  
def openFile():
  global ruta
  ruta = filedialog.askopenfilename(initialdir=os.getcwd())

def speech(summary:str):

  speech_file_path = os.getcwd() + "/summary_audios/" + sumary_name + ".mp3"

  response = client.audio.speech.create(
    model="tts-1-hd",
    voice="alloy",
    input= summary
  )

  response.stream_to_file(speech_file_path)
  
  playsound(speech_file_path)

def keywords(resset, key_word:list, input:str):
  
  if resset == 1:
    if len(key_word) <= 5:
      
      key_word.append(input)
      
    print(key_word)
    
  if resset == 0:  
    key_word.clear()
    print(key_word)
    

#==============================================================================================================================
#INICIALIZAMOS VALORES POR DEFECTO  
texto_size = ""
prompt_type = "Academico"
key_word = []

#==============================================================================================================================
#INICIALIZAMOS VENTANA
#------------------------------------------------------------------------------------------
#ventana principal
ventana = Tk()

icono = PhotoImage(file=os.getcwd()+"\img\ICO.png")
ventana.iconphoto(True, icono)

ventana.config(
  background="SlateGray4"
  )

ventana.title("Resaud")

#------------------------------------------------------------------------------------------
#Marcos
marco1 = LabelFrame(
  ventana,
  width=70,
  height=15,
  bg="SlateGray3",
  padx=10,
  pady=10,
  borde=0,
)

marco2 = LabelFrame(
  ventana,
  width=70,
  height=15,
  bg="SlateGray3",
  padx=10,
  pady=10,  
  borde=0,
)

#------------------------------------------------------------------------------------------
#logo
# Carga la imagen
img = Image.open(os.getcwd()+"\img\LOGO.png")

# Redimensiona la imagen
img = img.resize((150, 150), Image.Resampling.LANCZOS)

# Crea un objeto PhotoImage con la imagen redimensionada
img_tk = ImageTk.PhotoImage(img)


# Crear un widget Label y establecer la imagen como su contenido
logo = Label(marco1, image=img_tk)
logo.config(
  border=10,
  padx=5,
)

#------------------------------------------------------------------------------------------
#Ventanas de texto
ventana_texto01 = Text(marco2)
ventana_texto01.config(
  width=35, 
  height=30, 
  background="gray99",
  border=2,
  font=("Cascadia Code",12)
)

ventana_texto02 = Text(marco2)
ventana_texto02.config(
  width=35, 
  height=30, 
  background="gray99",
  border = 2,
  font=("Cascadia Code",12)

)

#------------------------------------------------------------------------------------------
#Botones y funciones
buttonOpenFile = Button(marco1,text="Seleccionar Audio",command=openFile, font=("Cascadia Code",12))

buttonTranscribe = Button(marco1,text="Transcribir", command=lambda: transcribir("base", ruta,ventana, ventana_texto01), font=("Cascadia Code",12))

buttonResumir = Button(marco1,text="Resumir", command=lambda: resumir(MODEL_VERSION,Transcripcion, ventana, ventana_texto02, prompt_type, key_word), font=("Cascadia Code",12))

buttonAudio = Button(marco1,text="Escuchar", command=lambda: speech(summary=sumary.choices[0].message.content), font=("Cascadia Code",12))

buttonSEND = Button(marco1, text="Añadir", command=lambda: keywords(resset=1, key_word=key_word,input=valor.get()), font=("Cascadia Code",12))

buttonRESET = Button(marco1, text="Borrar", command=lambda: keywords(resset=0, key_word=key_word,input=valor.get()), font=("Cascadia Code",12))

#------------------------------------------------------------------------------------------
#Selectores 
prompt_selector = ttk.Combobox(
  marco1, 
  values= ["Academico", "Narrativo"], 
  width=10, 
  height=1,
  font=("Cascadia Code",12),
  )
prompt_selector.current(0)

size_selector = ttk.Combobox(
  marco1, 
  values=["Largo (25%)", "Medio (15%)", "Corto (10%)"], 
  width=11, 
  height=1,  
  font=("Cascadia Code",12)
)
size_selector.current(1)

#------------------------------------------------------------------------------------------
# Crea una variable StringVar para añadir keywords
valor = StringVar()
keyword_in = Entry(
  marco1, 
  textvariable=valor,  
  font=("Cascadia Code",12)
)

#------------------------------------------------------------------------------------------
#Ajustamos tamanhos
marco1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
marco2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")


ventana_texto01.grid(row=0, column=0,padx=10, pady=10)
ventana_texto02.grid(row=0, column=1,padx=10, pady=10)


logo.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
buttonOpenFile.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
buttonTranscribe.grid(row=2, column=0, columnspan=2, padx=10, pady=10)
prompt_selector.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
size_selector.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

keyword_in.grid(row=5, column=0, columnspan=2, padx=10, pady=10)
buttonSEND.grid(row=6, column=0, padx=10, pady=10)
buttonRESET.grid(row=6, column=1, padx=10, pady=10)

buttonResumir.grid(row=7, column=0,  columnspan=2, padx=10, pady=10)
buttonAudio.grid(row=8, column=0,  columnspan=2, padx=10, pady=10)

#------------------------------------------------------------------------------------------
#GENERAMOS VENTANA
ventana.mainloop()