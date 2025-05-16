from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 🛡️ Tokens
DIGISAC_TOKEN = "Bearer fdb36d7ef9c813c6516ff7fae664a529199b4311"
OPENAI_TOKEN = Bearer "sk-proj-sl..."
# 🔧 Permitir POST mesmo sem content-type correto
@app.before_request
def permitir_tudo():
    if request.method == 'POST' and request.path == '/webhook':
        if not request.content_type or 'application/json' not in request.content_type:
            request.environ['CONTENT_TYPE'] = 'application/json'

@app.route('/webhook', methods=['POST'], strict_slashes=False)
def webhook():
    try:
        # 🟢 Lê o corpo bruto da requisição
        raw_data = request.data.decode('utf-8')
        payload = json.loads(raw_data)
        print("📩 Webhook recebido:", payload)

        # 🔎 Extrair IDs do webhook
        mensagem_id = payload["data"]["message"]["id"]
        contact_id = payload["data"]["contactId"]
        print(f"🧾 mensagem_id: {mensagem_id} | contact_id: {contact_id}")

        # 1️⃣ Buscar texto da mensagem original no Digisac
        digisac_url = f"https://bsantos.digisac.biz/api/v1/messages?where[id]={mensagem_id}"
        digisac_headers = {
            "Authorization": f"Bearer {DIGISAC_TOKEN}",
            "Content-Type": "application/json"
        }
        r_digisac = requests.get(digisac_url, headers=digisac_headers)
        r_digisac.raise_for_status()
        mensagem = r_digisac.json()["data"][0]
        texto = mensagem.get("text", "")
        if not texto:
            return jsonify({"error": "Mensagem sem texto"}), 400

        print(f"💬 Texto recebido: {texto}")

        # 2️⃣ Enviar texto ao ChatGPT
        openai_payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Você é um atendente simpático do outlet Só Marcas."},
                {"role": "user", "content": texto}
            ],
            "temperature": 0.7
        }
        openai_headers = {
            "Authorization": f"Bearer {OPENAI_TOKEN}",
            "Content-Type": "application/json"
        }
        r_gpt = requests.post("https://api.openai.com/v1/chat/completions",
                              headers=openai_headers, json=openai_payload)
        r_gpt.raise_for_status()
        resposta = r_gpt.json()["choices"][0]["message"]["content"]
        print(f"🤖 Resposta do ChatGPT: {resposta}")

        # 3️⃣ Enviar resposta para o cliente via Digisac
        resposta_payload = {
            "text": resposta,
            "type": "chat",
            "contactId": contact_id,
            "origin": "bot"
        }
        r_envio = requests.post("https://bsantos.digisac.biz/api/v1/messages",
                                headers=digisac_headers, json=resposta_payload)
        r_envio.raise_for_status()
        print("📤 Resposta enviada com sucesso para o cliente.")

        return jsonify({
            "status": "mensagem respondida",
            "pergunta": texto,
            "resposta": resposta
        }), 200

    except Exception as e:
        print("❌ Erro:", str(e))
        return jsonify({"error": "Falha no processamento", "detalhe": str(e)}), 500
