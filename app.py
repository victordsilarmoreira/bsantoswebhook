from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Tokens
OPENAI_TOKEN = "Bearer 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"
DIGISAC_TOKEN = "Bearer fdb36d7ef9c813c6516ff7fae664a529199b4311"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Lê o JSON bruto
        payload = json.loads(request.data.decode("utf-8"))
        print("📩 Webhook recebido")

        # Extrai o texto e o contactId diretamente
        text = payload["data"]["message"]["text"]
        contact_id = payload["data"]["contactId"]
        print(f"💬 Texto: {text}")
        print(f"👤 contactId: {contact_id}")

        # Envia texto para OpenAI
        openai_url = "https://api.openai.com/v1/chat/completions"
        openai_headers = {
            "Authorization": f"Bearer {OPENAI_TOKEN}",
            "Content-Type": "application/json"
        }
        openai_payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.7
        }

        response_openai = requests.post(openai_url, headers=openai_headers, json=openai_payload)
        response_openai.raise_for_status()
        resposta = response_openai.json()["choices"][0]["message"]["content"]
        print(f"✅ Resposta do ChatGPT: {resposta}")

        # Envia resposta ao Digisac
        digisac_url = "https://bsantos.digisac.biz/api/v1/messages"
        digisac_headers = {
            "Authorization": f"Bearer {DIGISAC_TOKEN}",
            "Content-Type": "application/json"
        }
        mensagem_payload = {
            "text": resposta,
            "type": "chat",
            "contactId": contact_id,
            "origin": "bot"
        }

        response_digisac = requests.post(digisac_url, headers=digisac_headers, json=mensagem_payload)
        response_digisac.raise_for_status()
        print("📤 Resposta enviada ao Digisac com sucesso!")

        return jsonify({"status": "ok", "resposta": resposta}), 200

    except Exception as e:
        print("❌ Erro no processamento:", str(e))
        return jsonify({"error": str(e)}), 500
