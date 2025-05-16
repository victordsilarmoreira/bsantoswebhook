from flask import Flask, request, jsonify, render_template
import requests
import json

app = Flask(__name__)
logs = []

# Seus tokens
OPENAI_TOKEN = "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"
DIGISAC_TOKEN = "fdb36d7ef9c813c6516ff7fae664a529199b4311"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = json.loads(request.data.decode("utf-8"))
        text = payload["data"]["message"]["text"]
        contact_id = payload["data"]["contactId"]

        # Enviar para OpenAI
        resposta = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.7
            }
        ).json()["choices"][0]["message"]["content"]

        # Enviar para Digisac
        requests.post(
            "https://bsantos.digisac.biz/api/v1/messages",
            headers={
                "Authorization": f"Bearer {DIGISAC_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "text": resposta,
                "type": "chat",
                "contactId": contact_id,
                "origin": "bot"
            }
        )

        # Log local para monitoramento
        logs.append({"texto": text, "resposta": resposta})
        if len(logs) > 20:
            logs.pop(0)

        return jsonify({"status": "ok", "resposta": resposta}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/monitor')
def monitor():
    return jsonify(logs[-10:])

@app.route('/painel')
def painel():
    return render_template("painel.html")
