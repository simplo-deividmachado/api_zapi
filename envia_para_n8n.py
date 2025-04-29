import requests

WEBHOOK_URL = "https://n8n.simplobot.cloud/webhook/simplobot"

HEADERS = {
    "host": "n8n.simplobot.cloud",
    "x-real-ip": "144.22.155.131",
    "x-forwarded-for": "144.22.155.131",
    "x-forwarded-host": "n8n.simplobot.cloud",
    "x-forwarded-port": "443",
    "x-forwarded-proto": "https",
    "x-forwarded-ssl": "on",
    "connection": "close",
    "content-type": "application/json",
    "origin": "https://api.z-api.io",
    "server": "Z-API",
    "user-agent":
    "Mozilla/5.0 (iPad; CPU OS 13_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/111.0 Mobile/15E148 Safari/605.1.15",
    "z-api-token": "E8EE405F7E1427A0B039A227"
}


def enviar_para_webhook(contato):
    try:
        payload = {
            "isStatusReply": False,
            "chatLid": f"{contato['numero']}@lid",
            "connectedPhone": "5511961322161",
            "waitingMessage": False,
            "isEdit": False,
            "isGroup": False,
            "isNewsletter": False,
            "instanceId": "3E01CEDAA99BE0C3E8468E66062CE0C1",
            "messageId": "AUTO-GENERATED-ID",
            "phone": contato['numero'],
            "fromMe": False,
            "momment": 1745434549265,
            "status": "RECEIVED",
            "chatName": contato['nome'],
            "senderPhoto": None,
            "senderName": contato['nome'],
            "photo": None,
            "broadcast": False,
            "participantLid": None,
            "forwarded": False,
            "type": "ReceivedCallback",
            "fromApi": False,
            "text": {
                "message": contato['mensagem']
            }
        }

        response = requests.post(WEBHOOK_URL, json=payload, headers=HEADERS)
        print(
            f"\n✅ Enviado para webhook (status {response.status_code}): {response.text}"
        )

    except Exception as e:
        print(f"\n❌ Erro ao enviar para webhook: {e}")
