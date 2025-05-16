from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

DIGISAC_TOKEN = "fdb36d7ef9c813c6516ff7fae664a529199b4311"
OPENAI_TOKEN = "sk-proj-..."  # substitua pelo token completo

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # ⚠️ Lê o corpo cru da requisição
        raw_body = request.data.decode("utf-8")
        print("📥 RAW recebido:", raw_body)

        payload = json.loads(raw_body)

        mensagem_id = payload["data"]["message"]["id"]
        contact_id = payload["data"]["contactId"]

        # Buscar texto original via Digisac
        digisac_url = f"https://bsantos.digisac.biz/api/v1/messages?where[id]={mensagem_id}"
        headers_digisac = {
            "Authorization": f"Bearer {DIGISAC_TOKEN}",
            "Content-Type": "application/json"
        }
        resposta_digisac = requests.get(digisac_url, headers=headers_digisac)
        texto = resposta_digisac.json()["data"][0].get("text", "")

        if not texto:
            return jsonify({"error": "Texto da mensagem ausente"}), 400

        # Enviar para ChatGPT
        openai_payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.7
        }
        headers_openai = {
            "Authorization": f"Bearer {OPENAI_TOKEN}",
            "Content-Type": "application/json"
        }
        resposta_openai = requests.post("https://api.openai.com/v1/chat/completions",
                                        headers=headers_openai, json=openai_payload)
        resposta = resposta_openai.json()["choices"][0]["message"]["content"]

        # Responder via Digisac
        resposta_final = {
            "text": resposta,
            "type": "chat",
            "contactId": contact_id,
            "origin": "bot"
        }
        requests.post("https://bsantos.digisac.biz/api/v1/messages",
                      headers=headers_digisac, json=resposta_final)

        return jsonify({"status": "ok", "resposta": resposta}), 200

    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({"erro": str(e)}), 500
