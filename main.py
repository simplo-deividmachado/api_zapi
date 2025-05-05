from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging
from mensagem_handler import receber_mensagem
from audio_handler import transcrever_audio  # importando novo handler
import uvicorn

app = FastAPI()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variável global para armazenar a última mensagem
ultima_mensagem = None
lista = []

@app.get("/")
async def status():
    return {
        "status": "online",
        "message": "Webhook pronto para receber mensagens"
    }

@app.post("/")
async def webhook(request: Request):
    global ultima_mensagem

    try:
        if request.headers.get("content-type") != "application/json":
            logger.error("Requisição sem JSON")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Dados não são JSON"}
            )

        data = await request.json()
        if not data:
            logger.error("JSON vazio ou inválido")
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "JSON inválido"}
            )

        # Log dos headers e body
        logger.info("\n--- Dados Recebidos ---")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"JSON: {data}")

        # Se for áudio, desvia o fluxo
        if "audio" in data:
            dados_audio = {
                "senderName": data.get("senderName", "Desconhecido"),
                "phone": data.get("phone", ""),
                "audioUrl": data["audio"].get("audioUrl", "")
            }
            transcrever_audio(dados_audio)
            return {"status": "audio received"}

        # Caso contrário, trata como mensagem de texto
        texto = data.get("text", "")

        if isinstance(texto, dict):
            if "message" in texto:
                texto = texto["message"]
            else:
                texto = next(iter(texto.values()), "")
        elif not isinstance(texto, str):
            texto = str(texto)

        ultima_mensagem = {
            "senderName": data.get("senderName", "Desconhecido"),
            "phone": data.get("phone", ""),
            "message": texto.strip()
        }
        lista.append(ultima_mensagem)
        receber_mensagem(ultima_mensagem)

        print("\n=== Mensagem Recebida ===")
        print(f"Remetente:{ultima_mensagem['senderName']}")
        print(f"Telefone: {ultima_mensagem['phone']}")
        print(f"Mensagem: {ultima_mensagem['message']}\n")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

if __name__ == '__main__':
    print(lista)
    uvicorn.run(
        "main:app",
        reload=True
    )
