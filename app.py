from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Tokens
DIGISAC_TOKEN = "Bearer fdb36d7ef9c813c6516ff7fae664a529199b4311"
OPENAI_TOKEN = "Bearer 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" 

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Etapa 1: Receber o corpo bruto da requisição
        raw_data = request.data.decode("utf-8")
        payload = json.loads(raw_data)
        print("📩 Webhook recebido com sucesso.")
        print("📨 Payload:", json.dumps(payload, indent=2))

        # Etapa 2: Tentar extrair mensagem_id e contact_id com segurança
        try:
            mensagem_id = payload.get("data", {}).get("message", {}).get("id")
            contact_id = payload.get("data", {}).get("contactId")

            if not mensagem_id or not contact_id:
                print("⚠️ ID da mensagem ou contactId ausente.")
                return jsonify({"erro": "mensagem_id ou contact_id não encontrado"}), 400

            print(f"🔍 ID da mensagem: {mensagem_id}")
            print(f"👤 Contact ID: {contact_id}")
        except Exception as e:
            print("❌ Erro ao extrair dados do webhook:", str(e))
            return jsonify({"erro": "Falha ao extrair dados do webhook", "detalhe": str(e)}), 400

        # Etapa 3: Buscar texto da mensagem original no Digisac
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

        print(f"💬 Texto da mensagem: {texto}")

        # Etapa 4: Enviar texto ao

    except Exception as e:
        print("❌ Erro durante o processo:", str(e))
        return jsonify({"error": "Falha no processamento", "detalhe": str(e)}), 500
