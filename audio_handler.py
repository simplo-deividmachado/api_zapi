import os
import requests
import logging
from google.generativeai import GenerativeModel, configure
from mensagem_handler import receber_mensagem

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar a chave da API Gemini
GEMINI_API_KEY = "AIzaSyDInLLcjzUFOINXdONwyIAHd4r1G83GCDI"
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "A variável de ambiente GEMINI_API_KEY não está configurada.")

configure(api_key=GEMINI_API_KEY)


def transcrever_audio(dados_audio):
    try:
        sender_name = dados_audio.get("senderName", "Desconhecido")
        phone = dados_audio.get("phone", "")
        audio_url = dados_audio.get("audioUrl", "")

        if not audio_url:
            raise ValueError("URL do áudio não fornecida.")

        # Pasta onde o áudio será salvo
        pasta_audio = "audio"
        os.makedirs(pasta_audio, exist_ok=True)  # Cria a pasta se não existir

        # Nome completo do arquivo
        nome_arquivo = os.path.join(pasta_audio, f"{phone}_audio_recebido.ogg")

        # Baixar o áudio
        response = requests.get(audio_url)
        if response.status_code != 200:
            raise Exception(f"Falha ao baixar áudio: {response.status_code}")

        with open(nome_arquivo, "wb") as f:
            f.write(response.content)

        logger.info(f"Áudio salvo com sucesso em {nome_arquivo}.")

        # Agora lê os bytes do áudio
        with open(nome_arquivo, "rb") as audio_file:
            audio_bytes = audio_file.read()

        # Carrega o modelo Gemini
        model = GenerativeModel("gemini-2.0-flash")

        # Envia os bytes como input para o modelo
        gemini_response = model.generate_content([{
            "mime_type": "audio/ogg",
            "data": audio_bytes
        }, "Transcreva o conteúdo deste áudio."])

        transcricao = gemini_response.text.strip()

        logger.info(f"Transcrição recebida: {transcricao}")
        print("\n=== Mensagem Recebida ===")
        print(f"senderName: {sender_name}")
        print(f"phone: {phone}")
        print(f"Transcription: {transcricao}\n")

        receber_mensagem({
            "senderName": sender_name,
            "phone": phone,
            "message": transcricao
        })

        return {
            "senderName": sender_name,
            "phone": phone,
            "transcription": transcricao
        }

    except Exception as e:
        logger.error(f"Erro na transcrição de áudio: {str(e)}", exc_info=True)
        return {
            "senderName": dados_audio.get("senderName", "Desconhecido"),
            "phone": dados_audio.get("phone", ""),
            "transcription": "[Erro ao transcrever o áudio]"
        }
