rfrom flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Tokens
DIGISAC_TOKEN = "Bearer fdb36d7ef9c813c6516ff7fae664a529199b4311"
OPENAI_TOKEN = "BBearer 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"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Etapa 1: Receber o webhook
        raw_data = request.data.decode("utf-8")
        payload = json.loads(raw_data)
        print("📩 Webhook recebido com sucesso.")
        print("📨 Payload recebido:", json.dumps(payload, indent=2))

        mensagem_id = payload["data"]["message"]["id"]
        contact_id = payload["data"]["contactId"]

        print(f"🔍 ID da mensagem: {mensagem_id}")
        print(f"👤 Contact ID: {contact_id}")

        # Etapa 2: Buscar texto da mensagem original no Digisac
        print("📡 Buscando mensagem original no Digisac...")
        digisac_url = f"https://bsantos.digisac.biz/api/v1/messages?where[id]={mensagem_id}"
        headers_digisac = {
            "Authorization": f"Bearer {DIGISAC_TOKEN}",
            "Content-Type": "application/json"
        }
        r_digisac = requests.get(digisac_url, headers=headers_digisac)
        r_digisac.raise_for_status()
        resposta_json = r_digisac.json()
        print("📦 Resposta da API Digisac:", json.dumps(resposta_json, indent=2))

        mensagem = resposta_json["data"][0]
        texto = mensagem.get("text", "")

        if not texto:
            print("⚠️ A mensagem não contém texto.")
            return jsonify({"error": "Mensagem sem texto"}), 400

        print(f"💬 Texto recebido da mensagem: {texto}")

        # Etapa 3: Enviar para OpenAI (ChatGPT)
        print("🤖 Enviando mensagem para o ChatGPT...")
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
        r_gpt = requests.post("https://api.openai.com/v1/chat/completions",
                              headers=headers_openai, json=openai_payload)
        r_gpt.raise_for_status()
        resposta_openai = r_gpt.json()
        print("🧠 Resposta bruta da OpenAI:", json.dumps(resposta_openai, indent=2))

        resposta = resposta_openai["choices"][0]["message"]["content"]
        print(f"✅ Resposta gerada pelo ChatGPT: {resposta}")

        # Etapa 4: Enviar a resposta de volta ao cliente via Digisac
        print("📤 Enviando resposta ao Digisac...")
        resposta_payload = {
            "text": resposta,
            "type": "chat",
            "contactId": contact_id,
            "origin": "bot"
        }
        r_envio = requests.post("https://bsantos.digisac.biz/api/v1/messages",
                                headers=headers_digisac, json=resposta_payload)
        r_envio.raise_for_status()
        print("✅ Mensagem enviada ao cliente com sucesso via Digisac.")

        return jsonify({
            "status": "mensagem respondida",
            "pergunta": texto,
            "resposta": resposta
        }), 200

    except Exception as e:
        print("❌ Erro durante o processo:", str(e))
        return jsonify({"error": "Falha no processamento", "detalhe": str(e)}), 500
