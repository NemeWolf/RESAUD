import openai
import tiktoken
from config import OPEN_AI_API_KEY, TEMPERATURE_MEMORY, MODEL_VERSION
from typing import Optional

class ReportClass:
    """
        Esta clase genera un reporte detallado de los contenidos expuestos en la clase.
        Dado un texto de entrada genera como salida un reporte. 
    """
    def __init__(self): 
        
        try:
            openai.api_key = OPEN_AI_API_KEY
        except Exception as e:
            print(f"Ocurrió algún error con la API KEY: {e}") 
            
        
        self.temperature = TEMPERATURE_MEMORY
        self.model_name = MODEL_VERSION

    def num_tokens_from_string(self,string: str, encoding_name: Optional[str] = "gpt-3.5-turbo") -> int:
        """_contador_de_tokens_

        Args:
            string (str): Texto de entrada
            encoding_name (Optional[str], optional): _description_. Defaults to "gpt-3.5-turbo".

        Returns:
            int: Numero de tokens de salida
        """
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens
            
    def report_creation(self,text:str)->str:
        """_reporte_

        Args:
            text (str): Texto de entrada dado por el transcriptor. 

        Returns:
            str: reporte que se infirió a partir del texto. 
        """

        # Prompt
        prompt =f"Your task is to synthesize a comprehensive report based on transcribed text from a university lecture. Your report should distill the core subject matter, enumerate the key concepts discussed, and catalog noteworthy comments made during the session. Please proceed to construct a detailed report on the following text: {text}"
        messages = [{"role": "user", "content": prompt}]
        
        # API Call
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                temperature = self.temperature,
                messages=messages)   
        except Exception as e:
            print(f"Ocurrió algún error con el llamado a la API de OpenAI: {e}") 
            return ""
        
        # Response
        return  response.choices[0].message["content"]

    def send(
        self,
        prompt=None,
        text_data=None,
        chat_model="gpt-3.5-turbo",
        model_token_limit=4092,
        max_tokens=2500,
    ):
        """
        Send the prompt at the start of the conversation and then send chunks of text_data to ChatGPT via the OpenAI API.
        If the text_data is too long, it splits it into chunks and sends each chunk separately.

        Args:
        - prompt (str, optional): The prompt to guide the model's response.
        - text_data (str, optional): Additional text data to be included.
        - max_tokens (int, optional): Maximum tokens for each API call. Default is 2500.

        Returns:
        - list or str: A list of model's responses for each chunk or an error message.
        """

        # Check if the necessary arguments are provided
        if not prompt:
            return "Error: Prompt is missing. Please provide a prompt."
        if not text_data:
            return "Error: Text data is missing. Please provide some text data."

        # Initialize the tokenizer
        tokenizer = tiktoken.encoding_for_model(chat_model)

        # Encode the text_data into token integers
        token_integers = tokenizer.encode(text_data)

        # Split the token integers into chunks based on max_tokens
        chunk_size = max_tokens - len(tokenizer.encode(prompt))
        chunks = [
            token_integers[i : i + chunk_size]
            for i in range(0, len(token_integers), chunk_size)
        ]

        # Decode token chunks back to strings
        chunks = [tokenizer.decode(chunk) for chunk in chunks]

        responses = []
        messages = [
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": "To provide the context for the above prompt, I will send you text in parts. When I am finished, I will tell you 'ALL PARTS SENT'. Do not answer until you have received all the parts.",
            },
        ]

        for chunk in chunks:
            messages.append({"role": "user", "content": chunk})

            # Check if total tokens exceed the model's limit and remove oldest chunks if necessary
            while (
                sum(len(tokenizer.encode(msg["content"])) for msg in messages)
                > model_token_limit
            ):
                messages.pop(1)  # Remove the oldest chunk

            response = openai.ChatCompletion.create(model=chat_model, messages=messages)
            chatgpt_response = response.choices[0].message["content"].strip()
            responses.append(chatgpt_response)

        # Add the final "ALL PARTS SENT" message
        messages.append({"role": "user", "content": "ALL PARTS SENT"})
        response = openai.ChatCompletion.create(model=chat_model, messages=messages)
        final_response = response.choices[0].message["content"].strip()
        responses.append(final_response)

        return responses
    

    def read_data(self,file):
        """
        Reads the content of a file and returns it as a string.

        Args:
        - file (str): The path to the file to be read.

        Returns:
        - str: The content of the file.
        """
        # Open the file and read the text
        with open(file, "r", encoding="UTF-8") as f:
            text = f.read()
        return text