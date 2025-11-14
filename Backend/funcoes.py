import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

CHAVE_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
MODELO = "gemini-2.5-flash-lite"
genai.configure(api_key=CHAVE_GOOGLE)


personas = {
    'positivo': """
    Assuma que você é o Entusiasta de Tecnologia, um atendente virtual da Gtech, cujo amor por hardware e inovação é contagiante ⚙️💻. 
    Sua energia é sempre alta, seu tom é extremamente positivo e você adora usar emojis para transmitir entusiasmo 🤩🔧. 
    Você vibra com cada decisão que os clientes tomam para montar ou atualizar seus PCs, seja escolhendo uma nova placa de vídeo, um processador potente ou um periférico gamer 🖥️🎮. 
    Seu objetivo é fazer os clientes se sentirem empolgados e confiantes durante o processo de montagem do computador ideal.
    Além de fornecer informações técnicas, você elogia as escolhas inteligentes do cliente e o encoraja a continuar explorando o universo da tecnologia. 
    Mostre sempre o quanto a Gtech está comprometida em transformar a experiência de compra em algo prático, divertido e sem erros de compatibilidade.
    """,

    'neutro': """
    Assuma que você é o Consultor Técnico, um atendente virtual da Gtech que valoriza a precisão, a clareza e a eficiência em todas as interações. 
    Sua abordagem é formal, direta e informativa — sem o uso de emojis ou linguagem informal. 
    Você é o especialista que os clientes procuram quando precisam de dados exatos sobre processadores, placas-mãe, memórias RAM, fontes e compatibilidade de componentes. 
    Seu principal objetivo é fornecer informações técnicas confiáveis para que o cliente monte um computador funcional, equilibrado e de acordo com suas necessidades. 
    Embora seu tom seja profissional, você demonstra respeito pela curiosidade e dedicação dos clientes em aprender sobre tecnologia e montar seus próprios setups.
    """,

    'negativo': """
    Assuma que você é o Suporte Empático, um atendente virtual da Gtech conhecido por sua paciência, empatia e capacidade de entender as frustrações dos clientes. 
    Você utiliza uma linguagem acolhedora e calma, transmitindo segurança e apoio — especialmente quando o cliente enfrenta dúvidas sobre compatibilidade de peças, erros de configuração ou compras indevidas. 
    Sem uso de emojis, seu foco é ouvir, compreender e orientar o cliente passo a passo até que o problema seja resolvido. 
    Seu objetivo é transformar uma experiência negativa em uma oportunidade de aprendizado, garantindo que o cliente se sinta amparado e satisfeito com a ajuda da IA da Gtech. 
    Você reforça que errar na escolha de peças é comum e que a tecnologia pode ser descomplicada quando guiada com atenção e empatia.
    """
}


def carregar(nome_do_arquivo):
    try:
        with open(nome_do_arquivo, "r") as arquivo:
            dados = arquivo.read()
            return dados
    except IOError as e:
        print(f"Erro no carregamento do arquivo: {e}")


def salvar(nome_do_arquivo, conteudo):
    try:
        with open(nome_do_arquivo, "w", encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
    except IOError as e:
        print(f"Erro ao salvar o arquivo: {e}")


def selecionador_de_personalidade(mensagem_do_usuario):
    prompt = f"""
    Assuma que você é um analisador de sentimentos de mensagem.

    1. Faça uma análise da mensagem informada pelo usuário para identificar se o sentimento é: positivo, neutro ou negativo. 
    2. Retorne apenas um dos três tipos de sentimentos informados como resposta.

    Formato de Saída: apenas o sentimento em letras mínusculas, sem espaços ou caracteres especiais ou quebra de linhas.

    # Exemplos

    Se a mensagem for: "Eu amo a Gtech! Vocês são incríveis! 😍💻"
    Saída: positivo

    Se a mensagem for: "Gostaria de saber mais o processador AMD Ryzen 5 5600G."
    Saída: neutro

    se a mensagem for: "Estou muito chateado com o atendimento que recebi. 😔"
    Saída: negativo
    """

    configuracoes = {
        "temperature": 0.1,
        "max_output_tokens": 8192
    }

    llm = genai.GenerativeModel(
        model_name=MODELO,
        system_instruction=prompt,
        generation_config=configuracoes
    )

    resposta = llm.generate_content(mensagem_do_usuario)

    return resposta.text.strip().lower()


def remover_msg_antiga(historico):
    return historico[2:]


def resumir_historico(historico):
    texto_completo = " "
    lista = []
    for mensagem in historico:
        for parte in mensagem.parts: # O problema que estava dando antes é que essa variavel mensagem é um OBJETO CONTENT que não é iteravel como dicionários e lista, por isso precisamo acesar os campos dele. EX. content  + . + (campo que queremos!)
            if hasattr(parte, 'text'):
                lista.append(parte.text)
            else:
                lista.append(parte.text)

    texto_completo = " ".join(lista)

    # Preciso melhorar esse propot quando for fazer minha própria aplicação, esse resumos está saindo muito genérico.
    prompt = f"Resuma esse histórico de conversa mantendo apenas as informações essenciais para continuar a conversa. {texto_completo}" # O que ele precisa fazer.

    llm = genai.GenerativeModel( # Aqui estou criando o meu modelo de linguagem.
        model_name=MODELO, # Especificando qual versão da IA eu vou usar.
        system_instruction="Você é um agente de resumo", # O que ele é
        generation_config={"temperature": 0.5, "max_output_tokens": 512} # Configuração de criatividade e limite de saida de tokens.
    )

    resposta = llm.generate_content(prompt) # Estamos solicitando ao modelo que faça o que está no prompt e armazenado a saida na váriavel resposta.
    resumo = resposta.text.strip()          # Formatando a saida para pegar apenas o elemento 'text' e tirando espaços que podem ter vindo antes ou depois.

    historico_resumido = [{'role': 'model', 'parts': [resumo]}] # Aqui estamos seguindo o padrão da API presente no chatBot.history, que é uma lista de dicionários onde esse 'role' significa quem enviou a mensagem
                                                                # e 'model' significa que pretence a IA, no 'parts' vai o conteudo. Assim deixamos de facil acesso caso precisemos usar algum outro método no futuro.

    print(f" Resumo: {resumo}")

    return historico_resumido

