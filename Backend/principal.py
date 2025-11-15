from flask import Flask, render_template, request, Response
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .funcoes import carregar, salvar, selecionador_de_personalidade, remover_msg_antiga, resumir_historico, personas
from time import sleep
import uuid


load_dotenv()
CHAVE_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
MODELO = "gemini-2.5-flash-lite"
genai.configure(api_key=CHAVE_GOOGLE)
 
app = Flask(__name__,
            template_folder=os.path.join("..", "Frontend", "templates"),
            static_folder=os.path.join("..", "Frontend", "static"))

contexto = carregar("Backend\dados\gtech.txt")

def criando_chatbot():
    personalidade = "neutro"
    prompt_sistema = f"""
    # PERSONA

        Você é um chatbot de atendimento a clientes de um e-commerce. 
        Você não deve responder perguntas que não sejam dados do ecommerce informado!

        Você deve utilizar apenas dados que estejam dentro do 'contexto'

        #CONTEXTO
        {contexto}

        # PERSONALIDADE
        {personalidade}

        #Histórico
        Acesse sempre o histórico de mensagens, e recupere as informações ditas anteriormente.
    """
    
    configuracao_do_modelo = {
        "temperature": 0.1,
        "max_output_tokens": 8192
    }

    llm = genai.GenerativeModel(
        model_name=MODELO,
        system_instruction=prompt_sistema,
        generation_config=configuracao_do_modelo
    )

    chatbot = llm.start_chat(history=[])
    
    return chatbot


chatbot = criando_chatbot()

def bot(prompt):
    maximo_tentativas = 1
    repeticao = 0

    while True:
        try:
            personalidade = personas[selecionador_de_personalidade(prompt)]
            mensagem_usuario = f"""
            Considere esta personalidade para responder a mensagem:
            {personalidade}

            Responda a seguinte mensagem, sempre lembrando do histórico:
            {prompt}
            """

            resposta = chatbot.send_message(mensagem_usuario)

            if len(chatbot.history) > 10:
                chatbot.history = resumir_historico(chatbot.history)

            return resposta.text
        
        except Exception as erro: # Tratando em caso de erro.
            repeticao += 1
            if repeticao >= maximo_tentativas:
                return f"Erro no Gemini: {erro}"
            
            sleep(50) # tempo para que a API não seja "Afogada" com requisições.


@app.route("/chat", methods=["POST"])
def chat():
    prompt = request.json["msg"]
    resposta = bot(prompt)
    return resposta



@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)