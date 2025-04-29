from flask import Flask, request, jsonify
import logging
from mensagem_handler import receber_mensagem
from audio_handler import transcrever_audio  # importando novo handler

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variável global para armazenar a última mensagem
ultima_mensagem = None
lista = []


@app.route('/', methods=['POST', 'GET'])
def webhook():
    global ultima_mensagem

    if request.method == 'GET':
        return jsonify({
            "status": "online",
            "message": "Webhook pronto para receber mensagens"
        }), 200

    try:
        if not request.is_json:
            logger.error("Requisição sem JSON")
            return jsonify({
                "status": "error",
                "message": "Dados não são JSON"
            }), 400

        data = request.get_json()
        if not data:
            logger.error("JSON vazio ou inválido")
            return jsonify({
                "status": "error",
                "message": "JSON inválido"
            }), 400

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
            return jsonify({"status": "audio received"}), 200

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

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    print(lista)
    app.run(host='0.0.0.0', port=5000, debug=True)
